import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [
    (3, 3), (3, 2), (3, 1), (3, 0),
    (2, 3), (2, 2), (2, 1), (2, 0),
    (1, 3)
]
DAY0_WHEAT = [(1, 2), (1, 1), (1, 0), (0, 3), (0, 2)]

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

_MARKET_PARAMS = {
    "HIRE_TARGETS": {
        "0": 5,
        "1": 5,
        "2": 5,
        "3": 6,
        "4": 8,
        "5": 11,
        "6": 11,
        "7": 15,
        "8": 15,
        "9": 20
    },
    "MAX_COWS": 12,
    "MAX_STRAWBERRIES": 35,
    "MAX_MELONS": 20,
    "COW_MIN_MONEY": 500,
    "STRAW_MIN_MONEY": 250,
    "MELON_MIN_MONEY": 300,
    "SPOILER_URGENCY_THRESH": 60,
    "WEIGHT_URGENT_WATER": 2000,
    "WEIGHT_FEED_ANIMAL": 1600,
    "WEIGHT_CARE_ANIMAL": 1400,
    "WEIGHT_CLEAR_WEED": 1100,
    "WEIGHT_WATER_PLANT": 1000,
    "WEIGHT_HARVEST_LIVESTOCK": 950,
    "WEIGHT_COLLECT_FERTILIZER": 900,
    "WEIGHT_HARVEST_CROP": 850,
    "WEIGHT_BUILD_STRUCTURE": 750,
    "WEIGHT_PLACE_ANIMAL": 700,
    "WEIGHT_PLANT_SEED": 650
},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
}

_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

PARAMS = {
    "HIRE_TARGETS": {
        "0": 5,
        "1": 5,
        "2": 5,
        "3": 6,
        "4": 8,
        "5": 11,
        "6": 11,
        "7": 15,
        "8": 15,
        "9": 20
    },
    "MAX_COWS": 12,
    "MAX_STRAWBERRIES": 35,
    "MAX_MELONS": 20,
    "COW_MIN_MONEY": 500,
    "STRAW_MIN_MONEY": 250,
    "MELON_MIN_MONEY": 300,
    "SPOILER_URGENCY_THRESH": 60,
    "WEIGHT_URGENT_WATER": 2000,
    "WEIGHT_FEED_ANIMAL": 1600,
    "WEIGHT_CARE_ANIMAL": 1400,
    "WEIGHT_CLEAR_WEED": 1100,
    "WEIGHT_WATER_PLANT": 1000,
    "WEIGHT_HARVEST_LIVESTOCK": 950,
    "WEIGHT_COLLECT_FERTILIZER": 900,
    "WEIGHT_HARVEST_CROP": 850,
    "WEIGHT_BUILD_STRUCTURE": 750,
    "WEIGHT_PLACE_ANIMAL": 700,
    "WEIGHT_PLANT_SEED": 650
},
    "MAX_COWS": 12,
    "MAX_STRAWBERRIES": 40,
    "MAX_MELONS": 20,
    "COW_MIN_MONEY": 500,
    "STRAW_MIN_MONEY": 250,
    "MELON_MIN_MONEY": 300,
    "SPOILER_URGENCY_THRESH": 60,
    "WEIGHT_URGENT_WATER": 2000,
    "WEIGHT_FEED_ANIMAL": 1600,
    "WEIGHT_CARE_ANIMAL": 1400,
    "WEIGHT_CLEAR_WEED": 1200,
    "WEIGHT_WATER_PLANT": 1000,
    "WEIGHT_HARVEST_LIVESTOCK": 950,
    "WEIGHT_COLLECT_FERTILIZER": 900,
    "WEIGHT_HARVEST_CROP": 850,
    "WEIGHT_BUILD_STRUCTURE": 750,
    "WEIGHT_PLACE_ANIMAL": 700,
    "WEIGHT_PLANT_SEED": 650,
}

_FR_STATE = {
    0: {"last_step": -1, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}},
    1: {"last_step": -1, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}},
}

def _shape(func, x, T=None):
    x = max(0.0, float(x))
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "hinge":
        if not T or T <= 0: return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x

def _market_price(item, inventory):
    p = _MARKET_PARAMS.get(item)
    if not p: return 1
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(price)))

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

def _town_demand_now(obs, item, step):
    demand = 1 if item != "FERTILIZER" and step % 24 == 0 else 0
    if step % 4 != 0:
        return demand
    town = obs.get("town", {})
    for shop in list(town.get("unlocked_shops", [])):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand

def _update_opp_state(obs, step):
    seat = obs["player"]
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}}
        _FR_STATE[seat] = state

    opp_idx = 1 - obs["player"]
    farms = obs.get("farms", [])
    opp_farm = farms[opp_idx] if len(farms) > opp_idx else {}
    
    prev_plants = state.setdefault("opp_plants", {})
    prev_animals = state.setdefault("opp_animals", {})
    curr_plants = {}
    curr_animals = {}
    
    for y, row in enumerate(opp_farm.get("tiles", [])):
        for x, tile in enumerate(row or []):
            if isinstance(tile, dict):
                if tile.get("kind") == "PLANT":
                    crop = str(tile.get("crop", ""))
                    yu = int(tile.get("yield_units", 0) or 0)
                    curr_plants[(x, y)] = {"crop": crop, "yu": yu}
                elif tile.get("kind") in ["COOP", "PASTURE"] and "animal" in tile:
                    an = str(tile.get("animal", ""))
                    yu = int(tile.get("yield_units", 0) or 0)
                    curr_animals[(x, y)] = {"animal": an, "yu": yu}
                    
    opp_shed = state.setdefault("opp_shed", {})
    
    for pos, prev in prev_plants.items():
        crop = prev["crop"]
        prev_yu = prev["yu"]
        curr = curr_plants.get(pos)
        harvested = 0
        if curr is None and prev_yu > 0: harvested = prev_yu
        elif curr is not None and curr["crop"] == crop and curr["yu"] < prev_yu: harvested = prev_yu - curr["yu"]
        if harvested > 0: opp_shed[crop] = opp_shed.get(crop, 0) + harvested

    for pos, prev in prev_animals.items():
        an = prev["animal"]
        prev_yu = prev["yu"]
        curr = curr_animals.get(pos)
        harvested = 0
        if curr is not None and curr["animal"] == an and curr["yu"] < prev_yu: harvested = prev_yu - curr["yu"]
        if harvested > 0:
            item = "EGG" if an == "GOOSE" else "MILK" if an == "COW" else "WOOL"
            opp_shed[item] = opp_shed.get(item, 0) + harvested
            
    market_inv = obs.get("market", {}).get("inventory", {})
    prev_inv = state.get("prev_inv", {})
    last_action = state.get("last_action") or {}
    
    our_sales = {}
    for order in (last_action.get("market") or []):
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            qty = max(0, int(order[2]))
            our_sales[item] = our_sales.get(item, 0) + qty
            
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        curr = int(market_inv.get(item, 10000))
        prev = int(prev_inv.get(item, 10000))
        ours = our_sales.get(item, 0)
        opp_sales = max(0, curr - prev - ours)
        if opp_sales > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - opp_sales)
            
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        demand = _town_demand_now(obs, item, step)
        if demand > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - demand)
            
    state["opp_plants"] = curr_plants
    state["opp_animals"] = curr_animals
    state["prev_inv"] = dict(market_inv)
    state["last_step"] = step
    return state

def calculate_roi(obs, money, day):
    market_prices = obs.get("market", {}).get("prices", {})
    days_left = 30 - day
    
    # Costs
    wheat_cost = 10
    cow_cost = 400
    sheep_cost = 400
    straw_seed = 10
    melon_seed = 30
    
    # Prices
    milk_p = market_prices.get("MILK", 160)
    wool_p = market_prices.get("WOOL", 200)
    straw_p = market_prices.get("STRAWBERRY", 120)
    melon_p = market_prices.get("MELON", 250)
    
    # ROI: (Expected Profit / Cost) per day
    # Cow eats 1 wheat/day, yields 1 milk/day
    roi_cow = (milk_p - wheat_cost) / cow_cost if cow_cost > 0 else 0
    roi_sheep = (wool_p - wheat_cost) / sheep_cost if sheep_cost > 0 else 0
    
    # Strawberry: Yields ~3 over its lifetime (takes 5 days to yield first)
    roi_straw = (straw_p * 3 - straw_seed) / straw_seed / 6.0 if straw_seed > 0 else 0
    
    # Melon: Yields ~3 over its lifetime (takes 10 days to yield first)
    roi_melon = (melon_p * 3 - melon_seed) / melon_seed / 11.0 if melon_seed > 0 else 0
    
    return {
        "COW": roi_cow if days_left >= 5 else -1,
        "SHEEP": roi_sheep if days_left >= 5 else -1,
        "STRAWBERRY": roi_straw if days_left >= 6 else -1,
        "MELON": roi_melon if days_left >= 11 else -1
    }

def agent(obs):
    try:
        player = obs["player"]
        me = obs["farms"][player]
        private = obs["private"]
        day = obs["day"]
        hour = obs["hour"]
        step = obs["step"]
        
        state = _update_opp_state(obs, step)
        
        money = me["money"]
        tiles = me["tiles"]
        unlocked_quads = me["unlocked_quadrants"]
        num_quads = len(unlocked_quads)
        shed = private["shed"]
        seeds = private["seeds"]
        inventories = private["inventories"]
        market_prices = obs.get("market", {}).get("prices", {})
        
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
        num_melons = 0
        
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if t == "LOCKED": continue
                elif t is None: empty_unlocked_tiles.append((c, r))
                elif isinstance(t, dict):
                    kind = t.get("kind")
                    if kind == "WEED": weeds.append((c, r))
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
                        if crop == "MELON": num_melons += 1

        market_orders = []
        current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
        
        # 1. MARKET ORDERS (DYNAMIC ROI)
        if day == 0 and hour == 0:
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            for _ in range(5): market_orders.append(["HIRE"])
            market_orders.append(["BUY_ANIMAL", "COW", 2])
            market_orders.append(["BUY_ANIMAL", "SHEEP", 2])
            market_orders.append(["BUY_SEED", "MELON", 9])
            market_orders.append(["BUY_SEED", "WHEAT", 5])
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        elif day > 0:
            if hour == 0:
                target_hands = PARAMS["HIRE_TARGETS"].get(day, 23)
                hires_today = me.get("hires_today", 0)
                if hires_today < target_hands and money >= 5:
                    for _ in range(min(target_hands - hires_today, 10)): market_orders.append(["HIRE"])
                        
            if hour in [1, 6, 12, 18]:
                num_animals = num_cows + num_sheep
                target_feed = num_animals * 3 + 8 if day >= 5 else 6
                if current_wheat < target_feed and money > 35:
                    needed_wheat = target_feed - current_wheat
                    while needed_wheat > 0 and len(market_orders) < 3:
                        buy_qty = min(needed_wheat, 10)
                        market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                        needed_wheat -= buy_qty
                        
                # Dynamic Expansion
                roi = calculate_roi(obs, money, day)
                best_roi = max(roi, key=roi.get)
                
                if "NE" not in unlocked_quads and money >= 1150 and day >= 6:
                    market_orders.append(["BUY_LAND"]); money -= 1000
                elif "SW" not in unlocked_quads and money >= 2300 and day >= 10:
                    market_orders.append(["BUY_LAND"]); money -= 2000
                    
                cows_in_shed = shed.get("COW", 0)
                straw_seeds = seeds.get("STRAWBERRY", 0)
                melon_seeds = seeds.get("MELON", 0)
                
                # Adaptive Purchasing based on ROI
                if best_roi == "COW" and roi["COW"] > 0:
                    if (num_cows + cows_in_shed) < PARAMS["MAX_COWS"] and money >= PARAMS["COW_MIN_MONEY"] and len(market_orders) < 8:
                        market_orders.append(["BUY_ANIMAL", "COW", 1]); money -= 400; cows_in_shed += 1
                elif best_roi == "STRAWBERRY" and roi["STRAWBERRY"] > 0:
                    if (num_strawberries + straw_seeds) < PARAMS["MAX_STRAWBERRIES"] and money >= PARAMS["STRAW_MIN_MONEY"] and len(empty_unlocked_tiles) > 3:
                        buy_straw = min(10, PARAMS["MAX_STRAWBERRIES"] - (num_strawberries + straw_seeds))
                        market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])
                elif best_roi == "MELON" and roi["MELON"] > 0:
                    if (num_melons + melon_seeds) < PARAMS["MAX_MELONS"] and money >= PARAMS["MELON_MIN_MONEY"] and len(empty_unlocked_tiles) > 3:
                        buy_melon = min(10, PARAMS["MAX_MELONS"] - (num_melons + melon_seeds))
                        market_orders.append(["BUY_SEED", "MELON", buy_melon])

            # Spoiler Selling
            opp_shed = state.get("opp_shed", {})
            total_in_shed = sum(cnt for item, cnt in shed.items() if item not in ["COW", "SHEEP"])
            urgency = total_in_shed >= PARAMS["SPOILER_URGENCY_THRESH"]

            
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
                if len(market_orders) >= 10: break
                p_count = shed.get(prod, 0)
                if p_count > 0:
                    # Generalized spoiler: if opponent has >= 2 in shed, front-run them immediately!
                    if opp_shed.get(prod, 0) >= 2:
                        batch_size = p_count
                    elif urgency or day >= 27:
                        batch_size = 14 if day >= 27 else 12
                    elif market_prices.get(prod, 100) >= 80:
                        batch_size = 8
                    else:
                        batch_size = 4
                    sell_amt = min(p_count, batch_size)
                    if sell_amt > 0:
                        market_orders.append(["SELL", prod, sell_amt])
                        
        # 2. HUNGARIAN DISPATCH
        tasks = []
        for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
            if not is_fed: tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
            if not is_cared: tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
            if y_u > 0: tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
            if f_av: tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
                
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
                if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict)): target_animal = "COW"
                elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories if isinstance(inv, dict)): target_animal = "SHEEP"
            if target_animal:
                tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})
                
        if day == 0:
            for p in DAY0_PASTURES:
                if tiles[p[1]][p[0]] is None: tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
        else:
            desired_pastures = min(12, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
            total_structures = len(animals_on_board) + len(empty_structures)
            if total_structures < desired_pastures:
                for p in COMPACT_PASTURE_LAYOUT:
                    if total_structures >= desired_pastures: break
                    if p[0] >= 5 and "NE" not in unlocked_quads: continue
                    if p[1] >= 5 and "SW" not in unlocked_quads: continue
                    if tiles[p[1]][p[0]] is None:
                        tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
                        total_structures += 1

        if day == 0:
            if seeds.get("MELON", 0) > 0:
                for p in DAY0_MELONS:
                    if tiles[p[1]][p[0]] is None: tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
            if seeds.get("WHEAT", 0) > 0:
                for p in DAY0_WHEAT:
                    if tiles[p[1]][p[0]] is None: tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
        else:
            avail_straw_seeds = seeds.get("STRAWBERRY", 0)
            avail_melon_seeds = seeds.get("MELON", 0)
            avail_wheat_seeds = seeds.get("WHEAT", 0)
            pasture_set = set(COMPACT_PASTURE_LAYOUT)
            for ep in empty_unlocked_tiles:
                if ep in pasture_set: continue
                if avail_straw_seeds > 0:
                    tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "STRAWBERRY"})
                    avail_straw_seeds -= 1
                elif avail_melon_seeds > 0:
                    tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
                    avail_melon_seeds -= 1
                elif avail_wheat_seeds > 0:
                    tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
                    avail_wheat_seeds -= 1

        unit_actions = ["PASS"] * num_units
        if not tasks:
            state["last_action"] = {"farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"], "hands": unit_actions[1:] if len(unit_actions) > 1 else [], "market": market_orders}
            return state["last_action"]
            
        cost_matrix = []
        for u_idx, u_pos in enumerate(all_units):
            u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            u_wheat = u_inv.get("WHEAT", 0)
            u_row = []
            for t in tasks:
                effective_cost = -t["weight"] + (manhattan(u_pos, t["pos"]) * 8)
                if t["type"] == "FEED":
                    if u_wheat > 0: effective_cost -= 150
                    elif current_wheat == 0: effective_cost += 3000
                if t["type"] == "PLACE_ANIMAL":
                    an = t.get("animal")
                    if u_inv.get(an, 0) > 0: effective_cost -= 200
                    elif shed.get(an, 0) == 0: effective_cost += 3000
                u_row.append(effective_cost)
            cost_matrix.append(u_row)
            
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assigned_tasks = {r_i: tasks[c_i] for r_i, c_i in zip(row_ind, col_ind)}
            
        for u_idx in range(num_units):
            u_pos = all_units[u_idx]
            u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            u_produce = sum(v for k, v in u_inv.items() if k not in ["COW", "SHEEP", "WHEAT"])
            
            if u_produce >= 8:
                closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                unit_actions[u_idx] = ["DROP"] if u_pos in SHED_TILES else [get_move_toward(u_pos, closest_shed)]
                continue
                    
            if u_idx not in assigned_tasks:
                unit_actions[u_idx] = ["DROP"] if u_produce > 0 and u_pos in SHED_TILES else ["PASS"]
                continue
                
            t = assigned_tasks[u_idx]
            t_type, t_pos = t["type"], t["pos"]
            
            if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
                unit_actions[u_idx] = ["PICKUP", "WHEAT", min(5, shed.get("WHEAT", 0))] if u_pos in SHED_TILES else [get_move_toward(u_pos, min(SHED_TILES, key=lambda s: manhattan(u_pos, s)))]
                continue
                
            if t_type == "PLACE_ANIMAL":
                an = t.get("animal")
                if u_inv.get(an, 0) == 0 and shed.get(an, 0) > 0:
                    unit_actions[u_idx] = ["PICKUP", an, 1] if u_pos in SHED_TILES else [get_move_toward(u_pos, min(SHED_TILES, key=lambda s: manhattan(u_pos, s)))]
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

        state["last_action"] = {
            "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
            "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
            "market": market_orders
        }
        return state["last_action"]
        
    except Exception:
        farm = obs.get("farms", [])[obs["player"]]
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in farm.get("hands", [])], "market": []}
