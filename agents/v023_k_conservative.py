"""
Candidate V023-K: Conservative Succession
-----------------------------------------
Features:
1. V023-G Capital allocation core.
2. Conservative strawberry replacement: only replaces bushes when age >= 14 (leaving no active yield unharvested).
3. Waters all strawberries until strict lifespan cutoff.
4. Replants cleared tiles with Wheat on Days 22-26.
"""

import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [(3, 3), (3, 2), (3, 1), (3, 0), (2, 3), (2, 2), (2, 1)]
DAY0_WHEAT = [(2, 0), (1, 3), (1, 2), (1, 1), (1, 0)]

COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3),
    (6, 4), (6, 3), (6, 2),
    (7, 4), (7, 3),
]

WEIGHT_URGENT_WATER = 1800
WEIGHT_FEED_ANIMAL = 1400
WEIGHT_CARE_ANIMAL = 1300
WEIGHT_CLEAR_WEED = 1100
WEIGHT_WATER_PLANT = 1000
WEIGHT_HARVEST_LIVESTOCK = 950
WEIGHT_COLLECT_FERTILIZER = 900
WEIGHT_HARVEST_CROP = 880
WEIGHT_DIG_EXHAUSTED = 850
WEIGHT_PLANT_SEED = 820
WEIGHT_BUILD_STRUCTURE = 750
WEIGHT_PLACE_ANIMAL = 700

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_move_toward(current, target):
    cx, cy = current
    tx, ty = target
    if cx < tx: return "EAST"
    if cx > tx: return "WEST"
    if cy < ty: return "SOUTH"
    if cy > ty: return "NORTH"
    return "PASS"

def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    
    money = me["money"]
    tiles = me["tiles"]
    unlocked_quads = me["unlocked_quadrants"]
    num_quads = len(unlocked_quads)
    shed = private["shed"]
    seeds = private["seeds"]
    inventories = private["inventories"]
    market = obs.get("market", {})
    market_prices = market.get("prices", {})
    
    all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
    num_units = len(all_units)
    
    animals_on_board = []
    empty_structures = []
    plants_on_board = []
    weeds = []
    empty_unlocked_tiles = []
    
    num_cows = 0
    num_sheep = 0
    num_strawberries = 0
    num_wheat_plants = 0
    
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if t == "LOCKED":
                continue
            elif t is None:
                empty_unlocked_tiles.append((c, r))
            elif isinstance(t, dict):
                kind = t.get("kind")
                if kind == "WEED":
                    weeds.append((c, r))
                elif kind in ["COOP", "PASTURE"]:
                    an = t.get("animal")
                    if an:
                        fed = t.get("fed_today", False)
                        cared = t.get("cared_today", False)
                        fert = t.get("fertilizer_available", False)
                        yu = t.get("yield_units", 0)
                        animals_on_board.append((c, r, an, fed, cared, fert, yu))
                        if an == "COW": num_cows += 1
                        elif an == "SHEEP": num_sheep += 1
                    else:
                        empty_structures.append((c, r, kind))
                elif kind == "PLANT":
                    crop = t.get("crop")
                    wat = t.get("watered_today", False)
                    yu = t.get("yield_units", 0)
                    planted_day = t.get("planted_day", day)
                    age = day - planted_day
                    max_life = t.get("max_lifespan_step", 720)
                    unwat = t.get("consecutive_unwatered", 0)
                    plants_on_board.append((c, r, crop, wat, yu, age, max_life, unwat))
                    if crop == "STRAWBERRY": num_strawberries += 1
                    elif crop == "WHEAT": num_wheat_plants += 1

    num_animals = len(animals_on_board)
    market_orders = []
    
    # 1. CAPITAL ALLOCATION & MARKET ORDERS
    if day == 0 and hour == 0:
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["BUY_SEED", "MELON", 7])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        if hour == 0:
            if day < 6:
                target_hands = 2
            elif num_quads >= 3:
                target_hands = 12 if day >= 10 and money >= 300 else 8
            elif num_quads >= 2:
                target_hands = 6 if money >= 80 else 4
            else:
                target_hands = 2
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 2:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        elif hour == 1:
            current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
            target_feed = num_animals * 3 + 6 if day >= 6 else 6
            if current_wheat < target_feed and money > 40:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 4:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            if "NE" not in unlocked_quads and money >= 1400 and day >= 6:
                market_orders.append(["BUY_LAND"])
            elif "SW" not in unlocked_quads and money >= 2800 and day >= 9:
                market_orders.append(["BUY_LAND"])
                
            if day >= 6 and day <= 15 and num_animals < 15:
                cows_in_shed = shed.get("COW", 0)
                if (num_cows + cows_in_shed) < 11 and (len(empty_structures) > 0 or cows_in_shed < 2):
                    n_cows_to_buy = 2 if money >= 3200 else (1 if money >= 1500 else 0)
                    for _ in range(n_cows_to_buy):
                        if len(market_orders) < 8 and (num_cows + cows_in_shed) < 11:
                            market_orders.append(["BUY_ANIMAL", "COW", 1])
                            money -= 1500
                    
            if day >= 9 and day <= 20 and money >= 300:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if (num_strawberries + straw_seeds) < 42 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 42 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])
                    
            if day >= 22 and day <= 26 and money >= 100:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 45:
                    buy_wheat = min(10, 45 - (num_wheat_plants + wheat_seeds))
                    market_orders.append(["BUY_SEED", "WHEAT", buy_wheat])
            elif day >= 6 and day < 22:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 10 and money >= 100:
                    market_orders.append(["BUY_SEED", "WHEAT", 4])

        else:
            for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
                if len(market_orders) >= 10: break
                p_count = shed.get(prod, 0)
                if p_count > 0:
                    cur_price = market_prices.get(prod, 100)
                    batch_size = 8 if cur_price >= 80 else 4
                    if day >= 27: batch_size = 12
                    sell_amt = min(p_count, batch_size)
                    market_orders.append(["SELL", prod, sell_amt])

    # 2. TASK GENERATION
    tasks = []
    for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
        if not is_fed:
            tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
        if not is_cared:
            tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
        if y_u > 0:
            tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
        if f_av:
            tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
            
    for (px, py, crop, is_wat, y_u, age, max_life, unwat) in plants_on_board:
        is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or \
                  (crop == "MELON" and age >= 10) or \
                  (crop in ["STRAWBERRY", "TOMATO"] and y_u > 0)
                  
        # Conservative cutoff: age >= 14
        is_exhausted_straw = (crop == "STRAWBERRY" and day >= 22 and age >= 14)
        
        if is_ripe and y_u > 0:
            tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif is_exhausted_straw and day <= 27:
            tasks.append({"type": "DIG", "pos": (px, py), "weight": WEIGHT_DIG_EXHAUSTED})
        elif not is_wat and not is_exhausted_straw:
            tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_URGENT_WATER if unwat >= 1 else WEIGHT_WATER_PLANT, "crop": crop})
            
    for (wx, wy) in weeds:
        tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
        
    for (sx, sy, skind) in empty_structures:
        target_animal = None
        if skind == "PASTURE":
            if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "COW"
            elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "SHEEP"
        if target_animal:
            tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})
            
    target_pasture_count = 4 if day < 6 else (8 if day < 8 else 15)
    current_pastures = len(animals_on_board) + len(empty_structures)
    if current_pastures < target_pasture_count and money > 300 and empty_unlocked_tiles:
        compact_candidates = [pt for pt in COMPACT_PASTURE_LAYOUT if pt in empty_unlocked_tiles]
        candidate_tiles = compact_candidates if compact_candidates else empty_unlocked_tiles
        for pt in candidate_tiles[:4]:
            tasks.append({"type": "BUILD_PASTURE", "pos": pt, "weight": WEIGHT_BUILD_STRUCTURE})
            
    avail_straw = seeds.get("STRAWBERRY", 0)
    avail_wheat = seeds.get("WHEAT", 0)
    avail_melon = seeds.get("MELON", 0)
    
    if (avail_straw > 0 or avail_wheat > 0 or avail_melon > 0) and empty_unlocked_tiles:
        reserved_for_pastures = set(COMPACT_PASTURE_LAYOUT) if current_pastures < target_pasture_count else set()
        interior_tiles = [(c, r) for (c, r) in empty_unlocked_tiles if (c, r) not in SHED_TILES and (c, r) not in reserved_for_pastures]
        for it in interior_tiles[:35]:
            chosen_crop = "WHEAT"
            if avail_melon > 0 and day < 5: chosen_crop = "MELON"
            elif avail_straw > 0 and day >= 8 and day < 21: chosen_crop = "STRAWBERRY"
            elif avail_wheat > 0 and day <= 27: chosen_crop = "WHEAT"
            else: chosen_crop = "WHEAT"
            
            if seeds.get(chosen_crop, 0) > 0:
                tasks.append({"type": "PLANT", "pos": it, "weight": WEIGHT_PLANT_SEED, "crop": chosen_crop})

    # 3. ACTION SELECTION & HUNGARIAN DISPATCH
    unit_actions = []
    
    if day == 0:
        for u_idx, upos in enumerate(all_units):
            inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            if u_idx == 0:
                if hour == 2 and upos in SHED_TILES and shed.get("SHEEP", 0) > 0:
                    unit_actions.append(["PICKUP", "SHEEP", 4]); continue
                elif hour == 3 and upos in SHED_TILES and shed.get("WHEAT", 0) > 0:
                    unit_actions.append(["PICKUP", "WHEAT", 4]); continue
                    
                t = tiles[upos[1]][upos[0]]
                if upos in DAY0_PASTURES:
                    if t is None: unit_actions.append(["BUILD_PASTURE"]); continue
                    elif isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal"):
                        if inv.get("SHEEP", 0) > 0: unit_actions.append(["PLACE", "SHEEP"]); continue
                    elif isinstance(t, dict) and t.get("animal"):
                        if not t.get("fed_today") and inv.get("WHEAT", 0) > 0: unit_actions.append(["FEED"]); continue
                        elif not t.get("cared_today"): unit_actions.append(["CARE"]); continue
                        
                next_p = None
                for pt in DAY0_PASTURES:
                    cur_t = tiles[pt[1]][pt[0]]
                    if cur_t is None or (isinstance(cur_t, dict) and (not cur_t.get("animal") or not cur_t.get("cared_today"))):
                        next_p = pt; break
                unit_actions.append([get_move_toward(upos, next_p)] if next_p else ["PASS"])
            else:
                target_tile, target_crop = None, "MELON"
                for m_pos in DAY0_MELONS:
                    cur_t = tiles[m_pos[1]][m_pos[0]]
                    if (cur_t is None and seeds.get("MELON", 0) > 0) or (isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today")):
                        target_tile, target_crop = m_pos, "MELON"; break
                if not target_tile:
                    for w_pos in DAY0_WHEAT:
                        cur_t = tiles[w_pos[1]][w_pos[0]]
                        if (cur_t is None and seeds.get("WHEAT", 0) > 0) or (isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today")):
                            target_tile, target_crop = w_pos, "WHEAT"; break
                if target_tile:
                    if upos == target_tile:
                        cur_t = tiles[upos[1]][upos[0]]
                        if cur_t is None: unit_actions.append(["PLANT", target_crop])
                        elif isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today"): unit_actions.append(["WATER"])
                        else: unit_actions.append(["PASS"])
                    else:
                        unit_actions.append([get_move_toward(upos, target_tile)])
                else:
                    unit_actions.append(["PASS"])

    if not unit_actions:
        pre_actions = [None] * num_units
        for u_idx, upos in enumerate(all_units):
            inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            inv_wheat = inv.get("WHEAT", 0)
            
            if upos in SHED_TILES:
                holding_prods = sum(v for k, v in inv.items() if k not in ["WHEAT", "SHEEP", "COW", "GOOSE"])
                if holding_prods > 0:
                    pre_actions[u_idx] = ["DROP"]
                    continue
                if empty_structures and (shed.get("COW", 0) > 0 or shed.get("SHEEP", 0) > 0) and not (inv.get("COW") or inv.get("SHEEP")):
                    an_to_pick = "COW" if shed.get("COW", 0) > 0 else "SHEEP"
                    pre_actions[u_idx] = ["PICKUP", an_to_pick, 1]
                    continue
                if num_animals > 0 and inv_wheat < 3 and shed.get("WHEAT", 0) > 0:
                    wheat_to_pick = min(4, shed.get("WHEAT", 0))
                    pre_actions[u_idx] = ["PICKUP", "WHEAT", wheat_to_pick]
                    continue

        if not tasks:
            for u_idx, upos in enumerate(all_units):
                if pre_actions[u_idx]:
                    unit_actions.append(pre_actions[u_idx])
                elif u_idx < len(inventories) and inventories[u_idx] and upos not in SHED_TILES:
                    closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                    unit_actions.append([get_move_toward(upos, closest_shed)])
                elif upos in SHED_TILES and u_idx < len(inventories) and inventories[u_idx]:
                    unit_actions.append(["DROP"])
                else:
                    unit_actions.append(["PASS"])
        else:
            cost_matrix = []
            for u_idx, upos in enumerate(all_units):
                row = []
                inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
                inv_wheat = inv.get("WHEAT", 0)
                inv_count = sum(inv.values()) if isinstance(inv, dict) else 0
                
                for t in tasks:
                    dist = manhattan(upos, t["pos"])
                    score = t["weight"] - (dist * 10)
                    
                    if u_idx in [0, 1] and t["type"] in ["FEED", "CARE", "HARVEST_ANIMAL", "COLLECT_FERTILIZER", "BUILD_PASTURE", "PLACE_ANIMAL"]:
                        score += 300
                    elif u_idx >= 2 and t["type"] in ["WATER", "HARVEST_CROP", "PLANT", "DIG"]:
                        score += 200
                        
                    if t["type"] == "FEED" and inv_wheat == 0:
                        score -= 3000
                    if t["type"] == "PLACE_ANIMAL" and inv.get(t.get("animal", ""), 0) == 0:
                        score -= 3000
                    if inv_count >= 8 and t["type"] not in ["FEED", "CARE"]:
                        score -= 500
                    row.append(-score)
                cost_matrix.append(row)
                
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            assignment = {row: col for row, col in zip(row_ind, col_ind)}
            
            for u_idx, upos in enumerate(all_units):
                if pre_actions[u_idx]:
                    unit_actions.append(pre_actions[u_idx])
                    continue
                    
                if u_idx in assignment:
                    t = tasks[assignment[u_idx]]
                    t_pos = t["pos"]
                    t_type = t["type"]
                    inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
                    inv_count = sum(inv.values()) if isinstance(inv, dict) else 0
                    
                    if inv_count >= 8:
                        if upos in SHED_TILES:
                            unit_actions.append(["DROP"])
                        else:
                            closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                            unit_actions.append([get_move_toward(upos, closest_shed)])
                        continue
                        
                    if upos == t_pos:
                        if t_type == "FEED":
                            if inv.get("WHEAT", 0) > 0:
                                unit_actions.append(["FEED"])
                            elif upos in SHED_TILES and shed.get("WHEAT", 0) > 0:
                                unit_actions.append(["PICKUP", "WHEAT", 4])
                            else:
                                closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                                unit_actions.append([get_move_toward(upos, closest_shed)])
                        elif t_type == "CARE":
                            unit_actions.append(["CARE"])
                        elif t_type == "HARVEST_ANIMAL":
                            unit_actions.append(["HARVEST"])
                        elif t_type == "COLLECT_FERTILIZER":
                            unit_actions.append(["COLLECT_FERTILIZER"])
                        elif t_type == "WATER":
                            unit_actions.append(["WATER"])
                        elif t_type == "HARVEST_CROP":
                            unit_actions.append(["HARVEST"])
                        elif t_type == "DIG":
                            unit_actions.append(["DIG"])
                        elif t_type == "BUILD_PASTURE":
                            unit_actions.append(["BUILD_PASTURE"])
                        elif t_type == "PLACE_ANIMAL":
                            target_an = t.get("animal", "COW")
                            if inv.get(target_an, 0) > 0:
                                unit_actions.append(["PLACE", target_an])
                            elif upos in SHED_TILES and shed.get(target_an, 0) > 0:
                                unit_actions.append(["PICKUP", target_an, 1])
                            else:
                                closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                                unit_actions.append([get_move_toward(upos, closest_shed)])
                        elif t_type == "PLANT":
                            crop_to_plant = t.get("crop", "WHEAT")
                            if seeds.get(crop_to_plant, 0) > 0:
                                unit_actions.append(["PLANT", crop_to_plant])
                            else:
                                unit_actions.append(["PASS"])
                        else:
                            unit_actions.append(["PASS"])
                    else:
                        unit_actions.append([get_move_toward(upos, t_pos)])
                else:
                    if u_idx < len(inventories) and inventories[u_idx] and upos not in SHED_TILES:
                        closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                        unit_actions.append([get_move_toward(upos, closest_shed)])
                    elif upos in SHED_TILES and u_idx < len(inventories) and inventories[u_idx]:
                        unit_actions.append(["DROP"])
                    else:
                        unit_actions.append(["PASS"])

    farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
    hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
    
    return {
        "farmer": farmer_act,
        "hands": hands_act,
        "market": market_orders[:10]
    }
