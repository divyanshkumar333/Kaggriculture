"""
V022-A Replay-Inspired Industrial Opening Agent (Flawless Execution)

Key Mechanics Handled:
1. Day 0 Exact Sequence:
   - Market orders at Hour 0/1: 4 Sheep, 8 Wheat feed, 7 Melons, 5 Wheat, 2 Hands.
   - Main farmer picks up 4 Sheep and 4 Wheat at shed (4,4).
   - Main farmer constructs 4 Pastures at (4,4), (4,3), (4,2), (3,4), placing, feeding, and caring for all 4 Sheep on Day 0!
   - Hands plant & water the 7 Melons and 5 Wheat on interior tiles.
2. Days 1-30 Livestock Loop:
   - Every morning (Hour 0/1), workers at shed pick up Wheat (e.g. 4-6 units) to feed animals.
   - Collect Fertilizer ($100 base) from all animals and sell immediately for ~$400-$1500/day recurring subsidy.
   - Care for all animals daily (+1 bonus yield per day).
   - Feed all animals daily (100% survival).
   - Harvest Milk, Wool, and Eggs.
3. Liquidity Gated Expansion:
   - Day 6 (Wool Harvest): When cash >= $1,800, buy Quad 2, build 2-4 Pastures, buy Cows, scale hands to 5-6.
   - Day 10 (Melon Harvest): When cash >= $3,500, buy Quad 3, expand herd to 10-11 Cows, mass-plant Strawberries, scale hands to 8-12.
4. Hungarian Assignment with Inventory Awareness:
   - Workers carry Wheat for feeding.
   - Workers auto-drop full inventories at shed.
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from scipy.optimize import linear_sum_assignment

BOARD_SIZE = 10
SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [(4, 0), (4, 1), (3, 2), (2, 3), (1, 4), (2, 4), (3, 3)]
DAY0_WHEAT = [(3, 0), (3, 1), (2, 2), (1, 3), (0, 4)]

# Priority weights
WEIGHT_FEED_ANIMAL = 2500
WEIGHT_CARE_ANIMAL = 1800
WEIGHT_HARVEST_LIVESTOCK = 1600
WEIGHT_COLLECT_FERTILIZER = 1500
WEIGHT_WATER_PLANT = 1400
WEIGHT_HARVEST_CROP = 1200
WEIGHT_CLEAR_WEED = 1000
WEIGHT_PLACE_ANIMAL = 900
WEIGHT_BUILD_STRUCTURE = 800
WEIGHT_PLANT_SEED = 700

def get_quadrant(x: int, y: int) -> str:
    if x < 5 and y < 5: return "NW"
    if x >= 5 and y < 5: return "NE"
    if x < 5 and y >= 5: return "SW"
    return "SE"

def manhattan(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_move_toward(start: Tuple[int, int], target: Tuple[int, int]) -> str:
    sx, sy = start
    tx, ty = target
    if sx < tx: return "EAST"
    if sx > tx: return "WEST"
    if sy < ty: return "SOUTH"
    if sy > ty: return "NORTH"
    return "PASS"

def agent(obs: Dict[str, Any]) -> Dict[str, Any]:
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    
    step = obs["step"]
    day = obs["day"]
    hour = obs["hour"]
    money = me["money"]
    unlocked_quads = set(me["unlocked_quadrants"])
    
    farmer_pos = tuple(me["farmer"])
    hands_pos = [tuple(h) for h in me["hands"]]
    all_units = [farmer_pos] + hands_pos
    num_units = len(all_units)
    
    tiles = me["tiles"]
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inventories = private.get("inventories", [{} for _ in range(num_units)])
    
    market_orders = []
    
    # -------------------------------------------------------------------------
    # 1. ENTITY AUDIT
    # -------------------------------------------------------------------------
    animals_on_board = [] # (x, y, animal_type, is_fed, is_cared, fert_avail, yield_units)
    plants_on_board = []   # (x, y, crop, is_watered, yield_units, age, max_lifespan)
    empty_unlocked_tiles = []
    empty_structures = []  # (x, y, kind)
    weeds = []
    
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            q = get_quadrant(c, r)
            if q not in unlocked_quads:
                continue
            t = tiles[r][c]
            if t is None:
                empty_unlocked_tiles.append((c, r))
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "WEED":
                    weeds.append((c, r))
                elif k == "PLANT":
                    crop = t.get("crop")
                    is_wat = t.get("watered_today", False)
                    y_u = t.get("yield_units", 0)
                    p_day = t.get("planted_day", day)
                    age = day - p_day
                    plants_on_board.append((c, r, crop, is_wat, y_u, age, t.get("max_lifespan_step", 720)))
                elif k in ["PASTURE", "COOP"]:
                    an = t.get("animal")
                    if an:
                        is_fed = t.get("fed_today", False)
                        is_cared = t.get("cared_today", False)
                        f_av = t.get("fertilizer_available", False)
                        y_u = t.get("yield_units", 0)
                        animals_on_board.append((c, r, an, is_fed, is_cared, f_av, y_u))
                    else:
                        empty_structures.append((c, r, k))

    num_sheep = sum(1 for a in animals_on_board if a[2] == "SHEEP")
    num_cows = sum(1 for a in animals_on_board if a[2] == "COW")
    num_animals = len(animals_on_board)
    
    # -------------------------------------------------------------------------
    # 2. MARKET & ECONOMIC CONTROLLER
    # -------------------------------------------------------------------------
    if hour == 0 or (hour == 1 and not market_orders):
        # A) Instant Fertilizer Selling (Recurring Subsidy)
        fert_in_shed = shed.get("FERTILIZER", 0)
        if fert_in_shed > 0:
            market_orders.append(["SELL", "FERTILIZER", fert_in_shed])
            
        # B) Harvested Produce Selling
        for prod in ["MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
            p_count = shed.get(prod, 0)
            if p_count > 0:
                sell_qty = min(p_count, 10)
                market_orders.append(["SELL", prod, sell_qty])
                
        # C) Sell surplus wheat
        wheat_in_shed = shed.get("WHEAT", 0)
        feed_needed = max(4, num_animals * 2)
        if wheat_in_shed > feed_needed + 5:
            surplus = min(wheat_in_shed - feed_needed, 10)
            market_orders.append(["SELL", "WHEAT", surplus])
            
        # D) Day 0 Opening Macro
        if day == 0 and hour == 0:
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            market_orders.append(["HIRE"])
            market_orders.append(["HIRE"])
            market_orders.append(["BUY_SEED", "MELON", 7])
            market_orders.append(["BUY_SEED", "WHEAT", 5])
            market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            
        # E) Daily Feed Replenishment (Keep at least 2 days of feed)
        elif day > 0:
            current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories)
            target_feed = num_animals * 2 + 2
            if current_wheat < target_feed and money > 100:
                buy_amt = min(target_feed - current_wheat, 10)
                market_orders.append(["BUY_PRODUCT", "WHEAT", buy_amt])
                
            # F) Land Expansion Gating
            # Day 6 Wool Spike -> Quad 2 ($1,000)
            if "NE" not in unlocked_quads and money >= 1800 and day >= 6:
                market_orders.append(["BUY_LAND"])
                
            # Day 10 Melon Spike -> Quad 3 ($2,000)
            elif "SW" not in unlocked_quads and money >= 3500 and day >= 10:
                market_orders.append(["BUY_LAND"])
                
            # Quad 4 Endgame ($4,000)
            elif "SE" not in unlocked_quads and money >= 8000 and day >= 15:
                market_orders.append(["BUY_LAND"])
                
            # G) Livestock Expansion (Cows & Sheep)
            if day >= 6 and money >= 1500 and num_animals < 15:
                if num_cows < 11 and len(empty_structures) > 0:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                elif num_sheep < 4 and len(empty_structures) > 0:
                    market_orders.append(["BUY_ANIMAL", "SHEEP", 1])
                    
            # H) Seed Purchases
            if day >= 10 and day <= 24 and money >= 800:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if straw_seeds < 8:
                    market_orders.append(["BUY_SEED", "STRAWBERRY", 4])
            elif day >= 1 and day <= 26:
                wheat_seeds = seeds.get("WHEAT", 0)
                if wheat_seeds < 6 and money >= 200:
                    market_orders.append(["BUY_SEED", "WHEAT", 4])
                    
            # I) Daily Labor Hiring (Progressive scaling)
            hires_today = me.get("hires_today", 0)
            target_hands = 2
            if day >= 6 and day < 10:
                target_hands = 5 if num_animals >= 4 else 3
            elif day >= 10 and day < 25:
                target_hands = 8 if money > 3000 else 5
                if money > 15000 and (len(plants_on_board) + num_animals) > 30:
                    target_hands = 11
            elif day >= 25:
                target_hands = 8
                
            if hires_today < target_hands and money > 100:
                needed = target_hands - hires_today
                for _ in range(min(needed, 5)):
                    market_orders.append(["HIRE"])

    # -------------------------------------------------------------------------
    # 3. TASK GENERATION FOR SPATIAL DISPATCH
    # -------------------------------------------------------------------------
    tasks = []
    
    # A) Animal Tasks (Feed, Care, Milk, Wool, Fertilizer)
    for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
        if not is_fed:
            tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
        if not is_cared:
            tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
        if y_u > 0:
            tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
        if f_av:
            tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
            
    # B) Plant Tasks (Water, Harvest)
    for (px, py, crop, is_wat, y_u, age, max_life) in plants_on_board:
        is_ripe = False
        if crop == "WHEAT" and age >= 2: is_ripe = True
        elif crop == "CARROT" and age >= 2: is_ripe = True
        elif crop == "MELON" and age >= 10: is_ripe = True
        elif crop in ["STRAWBERRY", "TOMATO"] and y_u > 0: is_ripe = True
        
        if is_ripe and y_u > 0:
            tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif not is_wat:
            tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_WATER_PLANT, "crop": crop})
            
    # C) Clear Weeds
    for (wx, wy) in weeds:
        tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
        
    # D) Place Animals into Empty Structures
    for (sx, sy, skind) in empty_structures:
        target_animal = "COW" if skind == "PASTURE" and shed.get("COW", 0) > 0 else ("SHEEP" if shed.get("SHEEP", 0) > 0 else None)
        if target_animal:
            tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})
            
    # E) Build Pastures
    target_pasture_count = 4 if day < 6 else (8 if day < 10 else 12)
    current_pastures = len(animals_on_board) + len(empty_structures)
    if current_pastures < target_pasture_count and money > 600 and empty_unlocked_tiles:
        perimeter_tiles = [(c, r) for (c, r) in empty_unlocked_tiles if (c in [0, 4, 5, 9] or r in [0, 4, 5, 9]) and (c, r) not in SHED_TILES]
        candidate_tiles = perimeter_tiles if perimeter_tiles else empty_unlocked_tiles
        for pt in candidate_tiles[:2]:
            tasks.append({"type": "BUILD_PASTURE", "pos": pt, "weight": WEIGHT_BUILD_STRUCTURE})
            
    # F) Plant Seeds
    avail_straw = seeds.get("STRAWBERRY", 0)
    avail_wheat = seeds.get("WHEAT", 0)
    avail_melon = seeds.get("MELON", 0)
    
    if (avail_straw > 0 or avail_wheat > 0 or avail_melon > 0) and empty_unlocked_tiles:
        interior_tiles = [(c, r) for (c, r) in empty_unlocked_tiles if (c, r) not in SHED_TILES]
        for it in interior_tiles[:8]:
            chosen_crop = "WHEAT"
            if avail_melon > 0 and day < 5: chosen_crop = "MELON"
            elif avail_straw > 0 and day >= 10: chosen_crop = "STRAWBERRY"
            elif avail_wheat > 0: chosen_crop = "WHEAT"
            tasks.append({"type": "PLANT", "pos": it, "weight": WEIGHT_PLANT_SEED, "crop": chosen_crop})

    # -------------------------------------------------------------------------
    # 4. UNIT-BY-UNIT ACTIONS & HUNGARIAN DISPATCH
    # -------------------------------------------------------------------------
    unit_actions = []
    
    # Check if Day 0 special opening can be cleanly scripted for turn 0..23
    if day == 0:
        for u_idx, upos in enumerate(all_units):
            inv = inventories[u_idx]
            if u_idx == 0: # Main Farmer
                # Step 0..3: pickup sheep & wheat
                if hour == 2 and upos in SHED_TILES and shed.get("SHEEP", 0) > 0:
                    unit_actions.append(["PICKUP", "SHEEP", 4])
                    continue
                elif hour == 3 and upos in SHED_TILES and shed.get("WHEAT", 0) > 0:
                    unit_actions.append(["PICKUP", "WHEAT", 4])
                    continue
                
                # Check current tile for Day 0 pasture build/place/feed/care
                t = tiles[upos[1]][upos[0]]
                if upos in DAY0_PASTURES:
                    if t is None:
                        unit_actions.append(["BUILD_PASTURE"])
                        continue
                    elif isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal"):
                        if inv.get("SHEEP", 0) > 0:
                            unit_actions.append(["PLACE", "SHEEP"])
                            continue
                    elif isinstance(t, dict) and t.get("animal"):
                        if not t.get("fed_today") and inv.get("WHEAT", 0) > 0:
                            unit_actions.append(["FEED"])
                            continue
                        elif not t.get("cared_today"):
                            unit_actions.append(["CARE"])
                            continue
                
                # Find next unfinished Day 0 pasture
                next_p = None
                for pt in DAY0_PASTURES:
                    cur_t = tiles[pt[1]][pt[0]]
                    if cur_t is None or (isinstance(cur_t, dict) and (not cur_t.get("animal") or not cur_t.get("cared_today"))):
                        next_p = pt
                        break
                if next_p:
                    unit_actions.append([get_move_toward(upos, next_p)])
                    continue
            else:
                # Hands 1 and 2: Sweep plant melons and wheat
                # Find unwatered or unplanted melon/wheat
                target_tile = None
                target_crop = "MELON"
                for m_pos in DAY0_MELONS:
                    cur_t = tiles[m_pos[1]][m_pos[0]]
                    if cur_t is None and seeds.get("MELON", 0) > 0:
                        target_tile = m_pos
                        target_crop = "MELON"
                        break
                    elif isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today"):
                        target_tile = m_pos
                        target_crop = "MELON"
                        break
                        
                if not target_tile:
                    for w_pos in DAY0_WHEAT:
                        cur_t = tiles[w_pos[1]][w_pos[0]]
                        if cur_t is None and seeds.get("WHEAT", 0) > 0:
                            target_tile = w_pos
                            target_crop = "WHEAT"
                            break
                        elif isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today"):
                            target_tile = w_pos
                            target_crop = "WHEAT"
                            break
                            
                if target_tile:
                    if upos == target_tile:
                        cur_t = tiles[upos[1]][upos[0]]
                        if cur_t is None:
                            unit_actions.append(["PLANT", target_crop])
                        elif isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today"):
                            unit_actions.append(["WATER"])
                        else:
                            unit_actions.append(["PASS"])
                    else:
                        unit_actions.append([get_move_toward(upos, target_tile)])
                    continue

    # Days 1-30: Hungarian Assignment
    if not unit_actions:
        # Check morning pickup for workers at shed
        pre_actions = [None] * num_units
        for u_idx, upos in enumerate(all_units):
            inv = inventories[u_idx]
            inv_wheat = inv.get("WHEAT", 0)
            inv_total = sum(inv.values()) if isinstance(inv, dict) else 0
            
            # If at shed:
            if upos in SHED_TILES:
                # 1. If holding harvested products, drop them
                holding_prods = sum(v for k, v in inv.items() if k not in ["WHEAT", "SHEEP", "COW", "GOOSE"])
                if holding_prods > 0:
                    pre_actions[u_idx] = ["DROP"]
                    continue
                # 2. If holding sheep/cow to place, keep it
                # 3. If shed has animals and pastures are empty, pickup animal
                if empty_structures and (shed.get("COW", 0) > 0 or shed.get("SHEEP", 0) > 0) and not (inv.get("COW") or inv.get("SHEEP")):
                    an_to_pick = "COW" if shed.get("COW", 0) > 0 else "SHEEP"
                    pre_actions[u_idx] = ["PICKUP", an_to_pick, 1]
                    continue
                # 4. If livestock exist and unit has low wheat, pickup wheat for feeding
                if num_animals > 0 and inv_wheat < 3 and shed.get("WHEAT", 0) > 0:
                    wheat_to_pick = min(4, shed.get("WHEAT", 0))
                    pre_actions[u_idx] = ["PICKUP", "WHEAT", wheat_to_pick]
                    continue

        if not tasks:
            for u_idx, upos in enumerate(all_units):
                if pre_actions[u_idx]:
                    unit_actions.append(pre_actions[u_idx])
                elif inventories[u_idx] and upos not in SHED_TILES:
                    closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                    unit_actions.append([get_move_toward(upos, closest_shed)])
                elif upos in SHED_TILES and inventories[u_idx]:
                    unit_actions.append(["DROP"])
                else:
                    unit_actions.append(["PASS"])
        else:
            cost_matrix = []
            for u_idx, upos in enumerate(all_units):
                row = []
                inv = inventories[u_idx]
                inv_wheat = inv.get("WHEAT", 0)
                inv_count = sum(inv.values()) if isinstance(inv, dict) else 0
                
                for t in tasks:
                    dist = manhattan(upos, t["pos"])
                    score = t["weight"] - (dist * 15)
                    
                    # If FEED task but unit has NO wheat, heavy penalty
                    if t["type"] == "FEED" and inv_wheat == 0:
                        score -= 3000
                    # If PLACE_ANIMAL task but unit has NO animal, heavy penalty
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
                    inv = inventories[u_idx]
                    inv_count = sum(inv.values()) if isinstance(inv, dict) else 0
                    
                    # If inventory full, return to shed
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
                        elif t_type == "HARVEST_CROP":
                            unit_actions.append(["HARVEST"])
                        elif t_type == "WATER":
                            unit_actions.append(["WATER"])
                        elif t_type == "DIG":
                            unit_actions.append(["DIG"])
                        elif t_type == "BUILD_PASTURE":
                            unit_actions.append(["BUILD_PASTURE"])
                        elif t_type == "PLACE_ANIMAL":
                            an_item = t.get("animal", "SHEEP")
                            if inv.get(an_item, 0) > 0:
                                unit_actions.append(["PLACE", an_item])
                            elif upos in SHED_TILES and shed.get(an_item, 0) > 0:
                                unit_actions.append(["PICKUP", an_item, 1])
                            else:
                                closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                                unit_actions.append([get_move_toward(upos, closest_shed)])
                        elif t_type == "PLANT":
                            unit_actions.append(["PLANT", t.get("crop", "WHEAT")])
                        else:
                            unit_actions.append(["PASS"])
                    else:
                        # If unit needs wheat to feed and is currently near shed, pickup first
                        if t_type == "FEED" and inv.get("WHEAT", 0) == 0 and upos in SHED_TILES and shed.get("WHEAT", 0) > 0:
                            unit_actions.append(["PICKUP", "WHEAT", 4])
                        elif t_type == "PLACE_ANIMAL" and inv.get(t.get("animal", ""), 0) == 0 and upos in SHED_TILES and shed.get(t.get("animal", ""), 0) > 0:
                            unit_actions.append(["PICKUP", t.get("animal", "SHEEP"), 1])
                        else:
                            unit_actions.append([get_move_toward(upos, t_pos)])
                else:
                    if inventories[u_idx] and upos not in SHED_TILES:
                        closest_shed = min(SHED_TILES, key=lambda s: manhattan(upos, s))
                        unit_actions.append([get_move_toward(upos, closest_shed)])
                    elif upos in SHED_TILES and inventories[u_idx]:
                        unit_actions.append(["DROP"])
                    else:
                        unit_actions.append(["PASS"])

    farmer_action = unit_actions[0] if unit_actions else ["PASS"]
    hands_actions = unit_actions[1:] if len(unit_actions) > 1 else []
    
    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market_orders[:10]
    }
