"""
Agent V026-B: GBDT-Guided Strategic Policy
------------------------------------------
Uses the decision splits extracted from LightGBM trained on top 1% trajectories:
1. Cow Expansion Trigger: Fired intra-day whenever money >= $480, cows < 9, day in [3..16],
   and working capital exceeds immediate feed requirements.
2. Strawberry Expansion Trigger: Fired whenever Q2 is unlocked and strawberry count < 40.
3. Adaptive Labor Allocator: Scales daily hires according to active livestock and crop count,
   strictly adhering to the 12-worker saturation ceiling.
4. Hard Safety Shield: Strict V025-A zero-starve, zero-weed, Hungarian assignment layer.
"""

import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [(3, 3), (3, 2), (3, 1), (3, 0), (2, 3), (2, 2), (2, 1), (2, 0), (1, 3)]
DAY0_WHEAT = [(1, 2), (1, 1), (1, 0), (0, 3), (0, 2)]

COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3),
    (6, 4), (6, 3), (6, 2),
    (7, 4), (7, 3),
]

WEIGHT_URGENT_WATER = 1900
WEIGHT_FEED_ANIMAL = 1500
WEIGHT_CARE_ANIMAL = 1400
WEIGHT_CLEAR_WEED = 1200
WEIGHT_WATER_PLANT = 1000
WEIGHT_HARVEST_LIVESTOCK = 950
WEIGHT_COLLECT_FERTILIZER = 900
WEIGHT_HARVEST_CROP = 850
WEIGHT_BUILD_STRUCTURE = 750
WEIGHT_PLACE_ANIMAL = 700
WEIGHT_PLANT_SEED = 650

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

def gbdt_predict_cow_purchase(day, money, num_cows, num_animals, current_wheat):
    # Rule distilled from GBDT feature splits: cows_d12, d0_cow_bought, money
    if day < 3 or day > 16:
        return False
    if num_cows >= 9:
        return False
    feed_buffer = num_animals * 2 + 6
    if current_wheat < feed_buffer:
        return False
    return money >= 480

def gbdt_predict_strawberry_purchase(day, money, num_strawberries, num_quads, empty_tiles):
    if day < 6 or day > 20:
        return False
    if num_quads < 2:
        return False
    if num_strawberries >= 40:
        return False
    if empty_tiles < 3:
        return False
    return money >= 240

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
    current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
    
    # 1. GBDT CAPITAL ALLOCATION
    if day == 0 and hour == 0:
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["BUY_ANIMAL", "COW", 1])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 3])
        market_orders.append(["BUY_SEED", "MELON", 9])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        if hour == 0:
            # GBDT Labor Curve
            if day == 1: target_hands = 4
            elif day < 4: target_hands = 3
            elif day < 6: target_hands = 4 if money >= 50 else 3
            elif num_quads >= 3: target_hands = 12 if day >= 10 and money >= 250 else 8
            elif num_quads >= 2: target_hands = 7 if money >= 80 else 5
            else: target_hands = 4
            
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 2:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        if hour in [1, 6, 12, 18]:
            target_feed = num_animals * 3 + 8 if day >= 5 else 6
            if current_wheat < target_feed and money > 35:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            if "NE" not in unlocked_quads and money >= 1150 and day >= 5:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2300 and day >= 8:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # GBDT Decision for Cow Expansion
            cows_in_shed = shed.get("COW", 0)
            if gbdt_predict_cow_purchase(day, money, num_cows + cows_in_shed, num_animals, current_wheat):
                while money >= 480 and (num_cows + cows_in_shed) < 9 and len(market_orders) < 8:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                    money -= 400
                    cows_in_shed += 1
                    
            # GBDT Decision for Strawberry Expansion
            straw_seeds = seeds.get("STRAWBERRY", 0)
            if gbdt_predict_strawberry_purchase(day, money, num_strawberries + straw_seeds, num_quads, len(empty_unlocked_tiles)):
                buy_straw = min(10, 40 - (num_strawberries + straw_seeds))
                market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])
                
            if day >= 22 and day <= 26 and money >= 100:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 35 and len(empty_unlocked_tiles) > 2:
                    market_orders.append(["BUY_SEED", "WHEAT", min(10, 35 - (num_wheat_plants + wheat_seeds))])

        for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(market_orders) >= 10: break
            p_count = shed.get(prod, 0)
            if p_count > 0:
                cur_price = market_prices.get(prod, 100)
                batch_size = 8 if cur_price >= 80 else 4
                if day >= 27: batch_size = 14
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
        if is_ripe and y_u > 0:
            tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif not is_wat:
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
            
    if day == 0:
        for p in DAY0_PASTURES:
            t = tiles[p[1]][p[0]]
            if t is None:
                tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
    else:
        desired_pastures = min(15, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
        total_structures = len(animals_on_board) + len(empty_structures)
        if total_structures < desired_pastures:
            for p in COMPACT_PASTURE_LAYOUT:
                if total_structures >= desired_pastures: break
                if p[0] >= 5 and "NE" not in unlocked_quads: continue
                if p[1] >= 5 and "SW" not in unlocked_quads: continue
                t = tiles[p[1]][p[0]]
                if t is None:
                    tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
                    total_structures += 1

    if day == 0:
        if seeds.get("MELON", 0) > 0:
            for p in DAY0_MELONS:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
        if seeds.get("WHEAT", 0) > 0:
            for p in DAY0_WHEAT:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
    else:
        avail_straw_seeds = seeds.get("STRAWBERRY", 0)
        avail_wheat_seeds = seeds.get("WHEAT", 0)
        pasture_set = set(COMPACT_PASTURE_LAYOUT)
        
        for ep in empty_unlocked_tiles:
            if ep in pasture_set: continue
            if avail_straw_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "STRAWBERRY"})
                avail_straw_seeds -= 1
            elif avail_wheat_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
                avail_wheat_seeds -= 1

    # 3. HUNGARIAN MATCHING
    unit_actions = ["PASS"] * num_units
    if not tasks:
        farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
        hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
        return {"farmer": [farmer_act] if isinstance(farmer_act, str) else farmer_act,
                "hands": [[h] if isinstance(h, str) else h for h in hands_act],
                "market": market_orders}
                
    cost_matrix = []
    for u_idx, u_pos in enumerate(all_units):
        u_costs = []
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        for t in tasks:
            dist = manhattan(u_pos, t["pos"])
            t_type = t["type"]
            base_w = t["weight"]
            
            penalty = 0
            if t_type == "FEED":
                has_wheat = u_inv.get("WHEAT", 0) > 0
                if not has_wheat:
                    dist_to_shed = min(manhattan(u_pos, sp) for sp in SHED_TILES)
                    penalty = dist_to_shed + 8
            elif t_type == "PLACE_ANIMAL":
                target_an = t["animal"]
                has_animal = u_inv.get(target_an, 0) > 0
                if not has_animal:
                    dist_to_shed = min(manhattan(u_pos, sp) for sp in SHED_TILES)
                    penalty = dist_to_shed + 8
                    
            c = (2000 - base_w) + (dist * 12) + penalty
            u_costs.append(c)
        cost_matrix.append(u_costs)
        
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    assigned_tasks = {r: tasks[c] for r, c in zip(row_ind, col_ind)}
    
    # 4. ACTION EXECUTION
    for u_idx, u_pos in enumerate(all_units):
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        
        if u_idx not in assigned_tasks:
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["PASS"]
            else:
                nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
            continue
            
        t = assigned_tasks[u_idx]
        t_pos = t["pos"]
        t_type = t["type"]
        
        if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0:
            if u_pos in SHED_TILES: unit_actions[u_idx] = ["PICKUP", "WHEAT", 1]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp)))]
            continue
            
        if t_type == "PLACE_ANIMAL":
            target_an = t["animal"]
            if u_inv.get(target_an, 0) == 0:
                if u_pos in SHED_TILES: unit_actions[u_idx] = ["PICKUP", target_an, 1]
                else: unit_actions[u_idx] = [get_move_toward(u_pos, min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp)))]
                continue
                
        if u_pos != t_pos:
            unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            continue
            
        if t_type == "FEED": unit_actions[u_idx] = ["FEED"]
        elif t_type == "CARE": unit_actions[u_idx] = ["CARE"]
        elif t_type == "WATER": unit_actions[u_idx] = ["WATER"]
        elif t_type in ["HARVEST_ANIMAL", "HARVEST_CROP"]: unit_actions[u_idx] = ["HARVEST"]
        elif t_type == "COLLECT_FERTILIZER": unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
        elif t_type == "DIG": unit_actions[u_idx] = ["DIG"]
        elif t_type == "BUILD_PASTURE": unit_actions[u_idx] = ["BUILD_PASTURE"]
        elif t_type == "PLACE_ANIMAL": unit_actions[u_idx] = ["PLACE", t["animal"], 1]
        elif t_type == "PLANT": unit_actions[u_idx] = ["PLANT", t["crop"]]
        else: unit_actions[u_idx] = ["PASS"]
            
    farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
    hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
    
    return {"farmer": farmer_act, "hands": hands_act, "market": market_orders}
