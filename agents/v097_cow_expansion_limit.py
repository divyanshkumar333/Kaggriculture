"""
Candidate V025-A: Aggressive Intra-Day Cow Velocity
---------------------------------------------------
Features:
1. Unlocks Cow purchasing from Day 4 onwards (as soon as cash >= $1,500 and pasture is available).
2. Intra-Day Purchasing: Evaluates cow purchases on EVERY hour as wool/milk/fertilizer revenue clears.
3. Removes the strict 2-cow/day limit (allows buying up to 4 cows/day when capital is available).
4. Maintains 3-Quadrant compact topology and Hungarian assignment core.
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
    
    # -------------------------------------------------------------------------
    # 1. CAPITAL ALLOCATION & MARKET ORDERS
    # -------------------------------------------------------------------------
    if day == 0 and hour == 0:
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["BUY_SEED", "MELON", 7])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        # -------------------------------------------------------------
        # STATE BRANCHING: MILK GLUT PIVOT
        # -------------------------------------------------------------
        milk_glut = market.get("inventory", {}).get("MILK", 0) > 60 or market_prices.get("MILK", 100) <= 50
        
        # LABOR SCALING AT HOUR 0
        if hour == 0:
            if milk_glut:
                # Pivot labor: massively surge workers to handle strawberries
                target_hands = 12 if money >= 100 else 8
            else:
                # Pre-pivot labor logic
                if day < 4:
                    target_hands = 2
                elif day < 6:
                    target_hands = 4 if money >= 50 else 2
                elif num_quads >= 2:
                    target_hands = 6 if money >= 80 else 4
                else:
                    target_hands = 3
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 2:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        # CAPITAL EXPANSION EVALUATED INTRA-DAY (Hours 1, 6, 12, 18)
        if hour in [1, 6, 12, 18]:
            current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
            target_feed = num_animals * 3 + 6 if day >= 5 else 6
            if current_wheat < target_feed and money > 40:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            # Quadrant Expansion (Q2 & Q3)
            if "NE" not in unlocked_quads and money >= 1200 and day >= 5:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2400 and day >= 8:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # Aggressive Cow Acceleration (Pre-Glut only)
            cows_in_shed = shed.get("COW", 0)
            if not milk_glut and day >= 4 and day <= 15 and (num_cows + cows_in_shed) < 11:
                if len(empty_structures) > 0 or cows_in_shed < 2:
                    while money >= 1500 and (num_cows + cows_in_shed) < 11 and len(market_orders) < 8:
                        market_orders.append(["BUY_ANIMAL", "COW", 1])
                        money -= 1500
                        cows_in_shed += 1
                        
            # Strawberry Seed Expansion (Post-Glut Pivot)
            if milk_glut and day >= 9 and day <= 24 and money >= 150:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if (num_strawberries + straw_seeds) < 42 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 42 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])
                    
            # Endgame Wheat Infill (Days 22-26)
            if day >= 22 and day <= 26 and money >= 150:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 35 and len(empty_unlocked_tiles) > 2:
                    market_orders.append(["BUY_SEED", "WHEAT", min(10, 35 - (num_wheat_plants + wheat_seeds))])

        # PACED DYNAMIC SELLING (All hours)
        for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(market_orders) >= 10: break
            p_count = shed.get(prod, 0)
            if p_count > 0:
                cur_price = market_prices.get(prod, 100)
                batch_size = 8 if cur_price >= 80 else 4
                if day >= 27: batch_size = 12
                sell_amt = min(p_count, batch_size)
                market_orders.append(["SELL", prod, sell_amt])

    # -------------------------------------------------------------------------
    # 2. TASK GENERATION FOR SPATIAL DISPATCH
    # -------------------------------------------------------------------------
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
            
    # Pasture Building Plan
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

    # Planting Seeds
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

    # -------------------------------------------------------------------------
    # 3. HUNGARIAN OPTIMAL TASK MATCHING
    # -------------------------------------------------------------------------
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
    
    assigned_tasks = {}
    for r, c in zip(row_ind, col_ind):
        assigned_tasks[r] = tasks[c]
        
    # -------------------------------------------------------------------------
    # 4. ACTION EXECUTION & SHED INTERACTION
    # -------------------------------------------------------------------------
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
        
        if t_type == "FEED":
            if u_inv.get("WHEAT", 0) == 0:
                if u_pos in SHED_TILES:
                    unit_actions[u_idx] = ["PICKUP", "WHEAT", 4]
                else:
                    nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                    unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
            else:
                if u_pos == t_pos:
                    unit_actions[u_idx] = ["FEED"]
                else:
                    unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
                    
        elif t_type == "PLACE_ANIMAL":
            target_an = t["animal"]
            if u_inv.get(target_an, 0) == 0:
                if u_pos in SHED_TILES:
                    unit_actions[u_idx] = ["PICKUP", target_an, 1]
                else:
                    nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                    unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
            else:
                if u_pos == t_pos:
                    unit_actions[u_idx] = ["PLACE", target_an, 1]
                else:
                    unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
                    
        elif t_type == "CARE":
            if u_pos == t_pos: unit_actions[u_idx] = ["CARE"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "HARVEST_ANIMAL":
            if u_pos == t_pos: unit_actions[u_idx] = ["HARVEST"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "COLLECT_FERTILIZER":
            if u_pos == t_pos: unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "WATER":
            if u_pos == t_pos: unit_actions[u_idx] = ["WATER"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "HARVEST_CROP":
            if u_pos == t_pos: unit_actions[u_idx] = ["HARVEST"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "DIG":
            if u_pos == t_pos: unit_actions[u_idx] = ["DIG"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "BUILD_PASTURE":
            if u_pos == t_pos: unit_actions[u_idx] = ["BUILD_PASTURE"]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        elif t_type == "PLANT":
            if u_pos == t_pos: unit_actions[u_idx] = ["PLANT", t["crop"]]
            else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            
        # Inventory dump when adjacent to shed carrying sellable items
        if u_pos in SHED_TILES:
            carried_sellable = sum(u_inv.get(p, 0) for p in ["MILK", "WOOL", "STRAWBERRY", "MELON", "FERTILIZER", "CARROT", "EGG"])
            if carried_sellable >= 3:
                unit_actions[u_idx] = ["DROP"]

    farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
    hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
    
    return {
        "farmer": [farmer_act] if isinstance(farmer_act, str) else farmer_act,
        "hands": [[h] if isinstance(h, str) else h for h in hands_act],
        "market": market_orders
    }
