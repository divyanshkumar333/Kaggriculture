import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"), "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

def _town_demand_now(obs, item, step):
    demand = 1 if item != "FERTILIZER" and step % 24 == 0 else 0
    if step % 4 != 0: return demand
    for shop in list(obs.get("town", {}).get("unlocked_shops", [])):
        prods = _SHOP_PRODUCTS.get(shop, ())
        if item in prods: demand += 2 if len(prods) == 1 else 1
    return demand

# V032 Grandmaster Opening: 1 Cow, 4 Sheep
DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4), (3, 3)]
DAY0_MELONS = [
    (2, 4), (2, 3), (2, 2), (2, 1), (2, 0),
    (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    (0, 4), (0, 3), (0, 2), (0, 1), (0, 0),
    (3, 2), (3, 1), (3, 0), (4, 1)
]
DAY0_WHEAT = []

COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3), (2, 2),
    (6, 4), (6, 3), (6, 2),
]

WEIGHT_URGENT_WATER = 2000
WEIGHT_FEED_ANIMAL = 1600
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
    
    # -------------------------------------------------------------------------
    # 1. MACRO STRATEGY & MARKET ORDERS
    # -------------------------------------------------------------------------
    if day == 0 and hour == 0:
        # V028 Hypothesis Opening: 1 Cow + 4 Sheep + 19 Melons + 4 Hires
        market_orders.append(["BUY_PRODUCT", "WHEAT", 5])
        for _ in range(4): # HIRE4
            market_orders.append(["HIRE"])
        market_orders.append(["BUY_ANIMAL", "COW", 1])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
        market_orders.append(["BUY_SEED", "MELON", 19])
        
    elif day > 0:
        # NOTEBOOK LABOR SCALING (Hour 0)
        if hour == 0:
            if day == 1: target_hands = 1 # Drops to 1 hire on Day 1
            elif day == 2: target_hands = 2
            elif day == 3: target_hands = 3
            elif day == 4: target_hands = 3
            elif day == 5: target_hands = 3
            elif day == 6: target_hands = 4
            elif day == 7: target_hands = 7
            elif day == 8: target_hands = 6
            elif day == 9: target_hands = 7
            elif day >= 10: target_hands = 10
            else: target_hands = 6
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 5:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        # CAPITAL EXPANSION & LAND (Hours 1, 6, 12, 18)
        if hour in [1, 6, 12, 18]:
            # Wheat Seeding (V16 secret sauce: grows 143 wheat to feed and sell!)
            wheat_seeds = seeds.get("WHEAT", 0)
            if day >= 1 and money >= 25:
                # Target maintaining ~12 wheat plants early, up to 18 later
                target_wheat = 12 if day < 8 else 18
                if (num_wheat_plants + wheat_seeds) < target_wheat and len(empty_unlocked_tiles) > 2:
                    buy_w = min(10, target_wheat - (num_wheat_plants + wheat_seeds))
                    market_orders.append(["BUY_SEED", "WHEAT", buy_w])

            # Buy Emergency Feed if we run out
            target_feed = num_animals * 3 + 8 if day >= 5 else 6
            if current_wheat < target_feed and money > 35:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            # Quadrant Unlocks
            if "NE" not in unlocked_quads and money >= 1150 and day >= 6:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2300 and day >= 10:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # Calibrated Cow Capacity (Notebook expansion: reaches 8 by D8)
            cows_in_shed = shed.get("COW", 0)
            if day >= 5 and day <= 15 and (num_cows + cows_in_shed) < 9:
                while money >= 500 and (num_cows + cows_in_shed) < 9 and len(market_orders) < 8:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                    money -= 400
                    cows_in_shed += 1
                    
            # Delayed Strawberry Powerhouse
            straw_seeds = seeds.get("STRAWBERRY", 0)
            if day >= 8 and day <= 20 and money >= 250:
                if (num_strawberries + straw_seeds) < 40 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 40 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])

        # ADAPTIVE SHED PACING & SELLING (WITH TRUE FRONT RUNNING)
        total_in_shed = sum(cnt for item, cnt in shed.items() if item not in ["COW", "SHEEP"])
        urgency = total_in_shed >= 60
        step = day * 24 + hour
        
        for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(market_orders) >= 10:
                break
            p_count = shed.get(prod, 0)
            if p_count > 0:
                cur_price = market_prices.get(prod, 100)
                demand_now = _town_demand_now(obs, prod, step)
                demand_next = _town_demand_now(obs, prod, step + 1)
                
                if cur_price <= 5 and (demand_now > 0 or demand_next > 0) and day < 28 and not urgency:
                    continue
                    
                if demand_now > 0 and not (urgency or day >= 27):
                    continue
                elif demand_next > 0 and cur_price > 5:
                    batch_size = p_count
                else:
                    if urgency or day >= 27:
                        batch_size = 14 if day >= 27 else 12
                    elif cur_price >= 80:
                        batch_size = 8
                    else:
                        batch_size = 4
                        
                sell_amt = min(p_count, batch_size)
                if sell_amt > 0:
                    market_orders.append(["SELL", prod, sell_amt])

    # -------------------------------------------------------------------------
    # 2. TASK GENERATION & PRIORITIZATION
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
        is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or (crop == "MELON" and age >= 10) or (crop in ["STRAWBERRY", "TOMATO"] and y_u > 0)
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
            if tiles[p[1]][p[0]] is None:
                tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
    else:
        desired_pastures = min(13, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
        total_structures = len(animals_on_board) + len(empty_structures)
        if total_structures < desired_pastures:
            for p in COMPACT_PASTURE_LAYOUT:
                if total_structures >= desired_pastures:
                    break
                if p[0] >= 5 and "NE" not in unlocked_quads: continue
                if p[1] >= 5 and "SW" not in unlocked_quads: continue
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
                    total_structures += 1

    if day == 0:
        if seeds.get("MELON", 0) > 0:
            for p in DAY0_MELONS:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
    else:
        avail_straw_seeds = seeds.get("STRAWBERRY", 0)
        avail_wheat_seeds = seeds.get("WHEAT", 0)
        pasture_set = set(COMPACT_PASTURE_LAYOUT)
        for ep in empty_unlocked_tiles:
            if ep in pasture_set:
                continue
            if avail_straw_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "STRAWBERRY"})
                avail_straw_seeds -= 1
            elif avail_wheat_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
                avail_wheat_seeds -= 1

    # -------------------------------------------------------------------------
    # 3. HUNGARIAN DISPATCH & MICRO EXECUTION
    # -------------------------------------------------------------------------
    unit_actions = ["PASS"] * num_units
    if not tasks:
        return {
            "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
            "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
            "market": market_orders
        }
        
    cost_matrix = []
    for u_idx, u_pos in enumerate(all_units):
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        u_wheat = u_inv.get("WHEAT", 0)
        u_row = []
        for t in tasks:
            dist = manhattan(u_pos, t["pos"])
            w = t["weight"]
            
            effective_cost = -w + (dist * 8)
            
            if t["type"] == "FEED":
                if u_wheat > 0:
                    effective_cost -= 150
                elif current_wheat == 0:
                    effective_cost += 3000
                    
            if t["type"] == "PLACE_ANIMAL":
                an = t.get("animal")
                if u_inv.get(an, 0) > 0:
                    effective_cost -= 200
                elif shed.get(an, 0) == 0:
                    effective_cost += 3000
                    
            u_row.append(effective_cost)
        cost_matrix.append(u_row)
        
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    assigned_tasks = {}
    for r_i, c_i in zip(row_ind, col_ind):
        assigned_tasks[r_i] = tasks[c_i]
        
    for u_idx in range(num_units):
        u_pos = all_units[u_idx]
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        
        u_produce = sum(v for k, v in u_inv.items() if k not in ["COW", "SHEEP", "WHEAT"])
        if u_produce >= 8:
            closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
                continue
            else:
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        if u_idx not in assigned_tasks:
            if u_produce > 0 and u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
            else:
                unit_actions[u_idx] = ["PASS"]
            continue
            
        t = assigned_tasks[u_idx]
        t_type = t["type"]
        t_pos = t["pos"]
        
        if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["PICKUP", "WHEAT", min(5, shed.get("WHEAT", 0))]
            else:
                closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
            continue
            
        if t_type == "PLACE_ANIMAL":
            an = t.get("animal")
            if u_inv.get(an, 0) == 0 and shed.get(an, 0) > 0:
                if u_pos in SHED_TILES:
                    unit_actions[u_idx] = ["PICKUP", an, 1]
                else:
                    closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                    unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        if u_pos == t_pos:
            if t_type == "FEED": unit_actions[u_idx] = ["FEED"]
            elif t_type == "CARE": unit_actions[u_idx] = ["CARE"]
            elif t_type in ["HARVEST_CROP", "HARVEST_ANIMAL"]: unit_actions[u_idx] = ["HARVEST"]
            elif t_type == "WATER": unit_actions[u_idx] = ["WATER"]
            elif t_type == "COLLECT_FERTILIZER": unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
            elif t_type == "DIG": unit_actions[u_idx] = ["DIG"]
            elif t_type == "BUILD_PASTURE": unit_actions[u_idx] = ["BUILD_PASTURE"]
            elif t_type == "PLACE_ANIMAL": unit_actions[u_idx] = ["PLACE", t.get("animal"), 1]
            elif t_type == "PLANT": unit_actions[u_idx] = ["PLANT", t.get("crop")]
            else: unit_actions[u_idx] = ["PASS"]
        else:
            unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]

    return {
        "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
        "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
        "market": market_orders
    }
