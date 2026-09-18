import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

WEIGHTS = {
    "WATER_CRITICAL": 2000,
    "FEED_CRITICAL": 1900,
    "CARE": 1600,
    "FEED_NORMAL": 1500,
    "HARVEST_CROP": 1200,
    "HARVEST_ANIMAL": 1100,
    "FERTILIZE": 1050,
    "WATER_NORMAL": 1000,
    "COLLECT_FERT": 950,
    "PLANT": 900,
    "BUILD": 800,
    "PLACE": 750,
    "DIG_WEED": 700,
}

_FR_STATE = {
    0: {"last_step": -1, "due": {}, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}},
    1: {"last_step": -1, "due": {}, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}},
}

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
    if step % 4 != 0: return demand
    town = obs.get("town", {})
    _SHOP_PRODUCTS = {
        "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
        "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
        "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
        "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"), "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
    }
    for shop in list(town.get("unlocked_shops", [])):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand

def _update_opp_state(obs, step):
    seat = obs["player"]
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due": {}, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}}
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
                    curr_plants[(x, y)] = {"crop": str(tile.get("crop", "")), "yu": int(tile.get("yield_units", 0) or 0)}
                elif tile.get("kind") in ["COOP", "PASTURE"] and "animal" in tile:
                    curr_animals[(x, y)] = {"animal": str(tile.get("animal", "")), "yu": int(tile.get("yield_units", 0) or 0)}
                    
    opp_shed = state.setdefault("opp_shed", {})
    for pos, prev in prev_plants.items():
        curr = curr_plants.get(pos)
        harvested = prev["yu"] if curr is None and prev["yu"] > 0 else (prev["yu"] - curr["yu"] if curr and curr["crop"] == prev["crop"] and curr["yu"] < prev["yu"] else 0)
        if harvested > 0: opp_shed[prev["crop"]] = opp_shed.get(prev["crop"], 0) + harvested
    for pos, prev in prev_animals.items():
        curr = curr_animals.get(pos)
        harvested = prev["yu"] - curr["yu"] if curr and curr["animal"] == prev["animal"] and curr["yu"] < prev["yu"] else 0
        if harvested > 0:
            item = "EGG" if prev["animal"] == "GOOSE" else "MILK" if prev["animal"] == "COW" else "WOOL"
            opp_shed[item] = opp_shed.get(item, 0) + harvested
            
    market_inv = obs.get("market", {}).get("inventory", {})
    prev_inv = state.get("prev_inv", {})
    last_action = state.get("last_action") or {}
    our_sales = {str(o[1]): sum(max(0, int(o2[2])) for o2 in (last_action.get("market") or []) if len(o2) >= 3 and o2[0] == "SELL" and o2[1] == o[1]) for o in (last_action.get("market") or []) if o[0] == "SELL"}
    
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        opp_sales = max(0, int(market_inv.get(item, 10000)) - int(prev_inv.get(item, 10000)) - our_sales.get(item, 0))
        if opp_sales > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - opp_sales)
        demand = _town_demand_now(obs, item, step)
        if demand > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - demand)
            
    state["opp_plants"] = curr_plants
    state["opp_animals"] = curr_animals
    state["prev_inv"] = dict(market_inv)
    state["last_step"] = step
    return state

def agent(obs):
    try:
        player = obs["player"]
        me = obs["farms"][player]
        private = obs["private"]
        day, hour, step = obs["day"], obs["hour"], obs["step"]
        state = _update_opp_state(obs, step)
        macro = state["macro"]
        
        money = me["money"]
        tiles = me["tiles"]
        shed = private["shed"]
        seeds = private["seeds"]
        inventories = private["inventories"]
        market_prices = obs.get("market", {}).get("prices", {})
        
        all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
        num_units = len(all_units)
        
        market_orders = []
        
        # MACRO STRATEGY (V057 AGGRESSIVE)
        if day == 0 and hour == 0:
            market_orders.append(["BUY_PRODUCT", "WHEAT", 34])
            for _ in range(11): market_orders.append(["HIRE"])
            market_orders.append(["BUY_ANIMAL", "COW", 2])
            market_orders.append(["BUY_SEED", "WHEAT", 20])
            macro["phase"] = 1 # Cow Engine
        elif day > 0:
            if hour == 0:
                hires_today = me.get("hires_today", 0)
                if macro["phase"] == 1 and hires_today < 11 and money >= 5:
                    for _ in range(min(11 - hires_today, 10)): market_orders.append(["HIRE"])
                elif macro["phase"] == 2 and hires_today < 15 and money >= 5:
                    for _ in range(min(15 - hires_today, 10)): market_orders.append(["HIRE"])
            
            if hour in [1, 6, 12, 18]:
                num_cows = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("animal") == "COW")
                num_wheat = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("crop") == "WHEAT")
                
                # Phase Transition
                if day >= 10 or num_cows >= 10: macro["phase"] = 2
                
                current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
                target_feed = num_cows * 3 + 5
                if current_wheat < target_feed and money > 35:
                    buy_qty = min(target_feed - current_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    
                if macro["phase"] == 1:
                    if money >= 400 and (num_cows + shed.get("COW", 0)) < 12:
                        market_orders.append(["BUY_ANIMAL", "COW", 1])
                    if num_wheat < 5 and money >= 10 and seeds.get("WHEAT", 0) == 0:
                        market_orders.append(["BUY_SEED", "WHEAT", 5])
                else:
                    if "SW" not in me["unlocked_quadrants"] and money >= 3000:
                        market_orders.append(["BUY_LAND"])
                    if money >= 250 and seeds.get("STRAWBERRY", 0) < 10:
                        market_orders.append(["BUY_SEED", "STRAWBERRY", 10])
                    if money >= 300 and seeds.get("MELON", 0) < 10:
                        market_orders.append(["BUY_SEED", "MELON", 10])

            # Advanced Spoiler Selling
            opp_shed = state.get("opp_shed", {})
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER"]:
                if len(market_orders) >= 10: break
                p_count = shed.get(prod, 0)
                if p_count > 0:
                    if opp_shed.get(prod, 0) >= 2 or day >= 27 or market_prices.get(prod, 100) >= 100:
                        sell_amt = min(p_count, 14 if day >= 27 else 8)
                        if sell_amt > 0: market_orders.append(["SELL", prod, sell_amt])

        # MICRO DYNAMIC DISPATCH (HUNGARIAN)
        tasks = []
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if isinstance(t, dict):
                    if t.get("kind") in ["COOP", "PASTURE"] and t.get("animal"):
                        an = t["animal"]
                        if not t.get("fed_today"): tasks.append({"type": "FEED", "pos": (c, r), "weight": WEIGHTS["FEED_CRITICAL"] if t.get("consecutive_unfed", 0) > 0 else WEIGHTS["FEED_NORMAL"], "animal": an})
                        if not t.get("cared_today"): tasks.append({"type": "CARE", "pos": (c, r), "weight": WEIGHTS["CARE"], "animal": an})
                        if t.get("yield_units", 0) > 0: tasks.append({"type": "HARVEST_ANIMAL", "pos": (c, r), "weight": WEIGHTS["HARVEST_ANIMAL"], "animal": an})
                        if t.get("fertilizer_available"): tasks.append({"type": "COLLECT_FERTILIZER", "pos": (c, r), "weight": WEIGHTS["COLLECT_FERT"], "animal": an})
                    elif t.get("kind") == "PLANT":
                        crop = t["crop"]
                        if t.get("yield_units", 0) > 0:
                            tasks.append({"type": "HARVEST_CROP", "pos": (c, r), "weight": WEIGHTS["HARVEST_CROP"], "crop": crop})
                        elif not t.get("watered_today"):
                            tasks.append({"type": "WATER", "pos": (c, r), "weight": WEIGHTS["WATER_CRITICAL"] if t.get("consecutive_unwatered", 0) > 0 else WEIGHTS["WATER_NORMAL"], "crop": crop})
                        if not t.get("fertilized_until_day", -1) >= day and shed.get("FERTILIZER", 0) > 0:
                            tasks.append({"type": "FERTILIZE", "pos": (c, r), "weight": WEIGHTS["FERTILIZE"], "crop": crop})
                    elif t.get("kind") == "WEED":
                        tasks.append({"type": "DIG", "pos": (c, r), "weight": WEIGHTS["DIG_WEED"]})
                    elif t.get("kind") == "PASTURE" and not t.get("animal") and shed.get("COW", 0) > 0:
                        tasks.append({"type": "PLACE_ANIMAL", "pos": (c, r), "weight": WEIGHTS["PLACE"], "animal": "COW"})
                elif t is None:
                    if day == 0 and (c, r) in [(4, 3), (4, 2), (3, 4), (3, 3)]:
                        tasks.append({"type": "BUILD_PASTURE", "pos": (c, r), "weight": WEIGHTS["BUILD"]})
                    elif seeds.get("WHEAT", 0) > 0:
                        tasks.append({"type": "PLANT", "pos": (c, r), "weight": WEIGHTS["PLANT"], "crop": "WHEAT"})
                    elif macro["phase"] == 2 and (seeds.get("STRAWBERRY", 0) > 0 or seeds.get("MELON", 0) > 0):
                        crop = "STRAWBERRY" if seeds.get("STRAWBERRY", 0) > 0 else "MELON"
                        tasks.append({"type": "PLANT", "pos": (c, r), "weight": WEIGHTS["PLANT"], "crop": crop})

        unit_actions = ["PASS"] * num_units
        if not tasks:
            state["last_action"] = {"farmer": unit_actions[0], "hands": unit_actions[1:], "market": market_orders}
            return state["last_action"]

        cost_matrix = []
        for u_idx, u_pos in enumerate(all_units):
            u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            u_wheat = u_inv.get("WHEAT", 0)
            u_row = []
            for t in tasks:
                effective_cost = -t["weight"] + (manhattan(u_pos, t["pos"]) * 20)
                if t["type"] == "FEED" and u_wheat == 0: effective_cost += 500
                if t["type"] == "FERTILIZE" and u_inv.get("FERTILIZER", 0) == 0: effective_cost += 500
                u_row.append(effective_cost)
            cost_matrix.append(u_row)
            
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assigned_tasks = {r_i: tasks[c_i] for r_i, c_i in zip(row_ind, col_ind)}
            
        for u_idx in range(num_units):
            if u_idx not in assigned_tasks: continue
            u_pos = all_units[u_idx]
            u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            t = assigned_tasks[u_idx]
            t_type, t_pos = t["type"], t["pos"]
            
            if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
                unit_actions[u_idx] = ["PICKUP", "WHEAT", 5] if u_pos in SHED_TILES else [get_move_toward(u_pos, min(SHED_TILES, key=lambda s: manhattan(u_pos, s)))]
                continue
            if t_type == "FERTILIZE" and u_inv.get("FERTILIZER", 0) == 0 and shed.get("FERTILIZER", 0) > 0:
                unit_actions[u_idx] = ["PICKUP", "FERTILIZER", 5] if u_pos in SHED_TILES else [get_move_toward(u_pos, min(SHED_TILES, key=lambda s: manhattan(u_pos, s)))]
                continue
            if t_type == "PLACE_ANIMAL" and u_inv.get(t["animal"], 0) == 0:
                unit_actions[u_idx] = ["PICKUP", t["animal"], 1] if u_pos in SHED_TILES else [get_move_toward(u_pos, min(SHED_TILES, key=lambda s: manhattan(u_pos, s)))]
                continue
                
            if u_pos == t_pos:
                if t_type == "FEED": unit_actions[u_idx] = ["FEED"]
                elif t_type == "CARE": unit_actions[u_idx] = ["CARE"]
                elif t_type in ["HARVEST_CROP", "HARVEST_ANIMAL"]: unit_actions[u_idx] = ["HARVEST"]
                elif t_type == "WATER": unit_actions[u_idx] = ["WATER"]
                elif t_type == "FERTILIZE": unit_actions[u_idx] = ["FERTILIZE"]
                elif t_type == "COLLECT_FERTILIZER": unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
                elif t_type == "DIG": unit_actions[u_idx] = ["DIG"]
                elif t_type == "BUILD_PASTURE": unit_actions[u_idx] = ["BUILD_PASTURE"]
                elif t_type == "PLACE_ANIMAL": unit_actions[u_idx] = ["PLACE", t["animal"], 1]
                elif t_type == "PLANT": unit_actions[u_idx] = ["PLANT", t["crop"]]
            else:
                unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]

        for u_idx, act in enumerate(unit_actions):
            if act[0] == "PASS" and all_units[u_idx] in SHED_TILES:
                u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
                if sum(u_inv.values()) > 0: unit_actions[u_idx] = ["DROP"]

        state["last_action"] = {"farmer": unit_actions[0], "hands": unit_actions[1:], "market": market_orders}
        return state["last_action"]
        
    except Exception as e:
        farm = obs.get("farms", [])[obs["player"]]
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in farm.get("hands", [])], "market": []}
