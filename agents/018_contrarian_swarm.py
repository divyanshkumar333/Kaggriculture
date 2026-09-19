def get_projected_prices(obs):
    shops = obs["town"]["unlocked_shops"]
    day = obs["day"]
    remaining_days = max(0, 30 - day)
    
    daily = {
        "WHEAT": 1, "CARROT": 1, "TOMATO": 1, 
        "STRAWBERRY": 1, "MELON": 1, "EGG": 1, 
        "MILK": 1, "WOOL": 1, "FERTILIZER": 0
    }
    
    for shop in shops:
        if shop == "PET_CAFE": daily["CARROT"] += 6
        if shop == "FARMERS_MARKET": 
            daily["CARROT"] += 3; daily["TOMATO"] += 3; daily["STRAWBERRY"] += 3; daily["WHEAT"] += 3
        if shop == "PIZZA_SHOP": 
            daily["TOMATO"] += 6; daily["WHEAT"] += 6; daily["MILK"] += 6
        if shop == "BAKERY": 
            daily["EGG"] += 6; daily["MILK"] += 6; daily["WHEAT"] += 12
        if shop == "BRUNCH_SPOT": 
            daily["EGG"] += 6; daily["STRAWBERRY"] += 6; daily["WHEAT"] += 6
        if shop == "ICE_CREAM_SHOP":
            daily["STRAWBERRY"] += 6; daily["MILK"] += 6; daily["WHEAT"] += 6
        if shop == "SMOOTHIE_SHOP":
            daily["STRAWBERRY"] += 6; daily["MILK"] += 6
        if shop == "CLOTHING_STORE":
            daily["WOOL"] += 12
            
    market_inv = obs["market"]["inventory"]
    
    def sim_price(item, inv):
        from kaggle_environments.envs.kaggriculture.kaggriculture import market_price
        return market_price(item, inv)
        
    projections = {}
    for item in ["CARROT", "TOMATO", "STRAWBERRY", "MELON"]:
        proj_inv = market_inv[item] - (daily[item] * remaining_days)
        projections[item] = sim_price(item, proj_inv)
        
    return projections

_STATE = {0: {}, 1: {}}

def agent(obs, configuration=None):
    player = obs["player"]
    step = obs["step"]
    day = obs["day"]
    me = obs["farms"][player]
    private = obs["private"]
    fx, fy = me["farmer"]
    
    state = _STATE[player]
    if step == 0:
        state.clear()
        state["best_crop"] = "TOMATO"
        state["swarm_plants"] = []
        
    market = []
    
    # Base Economy: 12-MELON
    melon_targets = [
        (0,0), (1,0), (2,0),
        (0,1), (1,1), (2,1),
        (0,2), (1,2), (2,2),
        (0,3), (1,3), (2,3)
    ]
    hand_melon_targets = [
        [(0,0), (1,0), (2,0)], # Hand 0
        [(0,1), (1,1), (2,1)], # Hand 1
        [(0,2), (1,2), (2,2)], # Hand 2
        [(0,3), (1,3), (2,3)], # Hand 3
    ]
    
    if step == 0:
        market.append(["BUY_SEED", "MELON", 12])
        
    melon_seeds_needed = 12 - private["seeds"].get("MELON", 0)
    if step > 0 and melon_seeds_needed > 0 and me["money"] >= melon_seeds_needed * 80 + 200:
        if not any(order[0] == "BUY_SEED" and order[1] == "MELON" for order in market):
            market.append(["BUY_SEED", "MELON", melon_seeds_needed])
    # Hire up to target_hands every day, 1 per turn
    target_hands = 4 # Base economy needs 4 hands
    if day >= 10:
        target_hands = 15 # Swarm needs up to 11 more
        
    def get_fib(n):
        if n <= 1: return 1
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
        
    if me["hires_today"] < target_hands and me["money"] >= get_fib(me["hires_today"]):
        market.insert(0, ["HIRE"])
        
    # Project prices and lock in best crop on day 15
    if step % 24 == 0 and day <= 15:
        projs = get_projected_prices(obs)
        state["best_crop"] = max(projs.keys(), key=lambda k: projs[k])
        
    best_crop = state["best_crop"]
    
    # Sell MELON continuously. Hoard best_crop until 718.
    if step < 718:
        melons = private["shed"].get("MELON", 0)
        if melons > 0:
            market.append(["SELL", "MELON", melons])
    else:
        for item, qty in private["shed"].items():
            if qty > 0:
                market.append(["SELL", item, qty])
                
    # Buy SW quadrant for swarm if needed
    if day >= 10 and "SW" not in me["unlocked_quadrants"] and me["money"] >= 2000:
        market.insert(0, ["BUY_LAND"])
        
    # Maintain seeds for best_crop
    seeds_needed = 20 - private["seeds"].get(best_crop, 0)
    if "SW" in me["unlocked_quadrants"] and seeds_needed > 0 and me["money"] >= 500:
        if not any(order[0] == "BUY_SEED" and order[1] == best_crop for order in market):
            market.append(["BUY_SEED", best_crop, seeds_needed])
            
    # Assign tasks to hands
    hands_actions = []
    
    def do_farmer(hx, hy, targets, crop, hand_idx, drop_loc=(4,4)):
        inv = private["inventories"][hand_idx+1] if hand_idx+1 < len(private["inventories"]) else {}
        # Drop if full or idle
        if sum(inv.values()) >= 5:
            if (hx, hy) != drop_loc:
                if hx < drop_loc[0]: return ["EAST"]
                elif hx > drop_loc[0]: return ["WEST"]
                elif hy < drop_loc[1]: return ["SOUTH"]
                elif hy > drop_loc[1]: return ["NORTH"]
            return ["DROP"]
            
        crop_stats = {
            "WHEAT": {"first_yield_day": 2, "max_yield_day": 4, "ongoing": False},
            "CARROT": {"first_yield_day": 2, "max_yield_day": 3, "ongoing": False},
            "TOMATO": {"first_yield_day": 8, "max_yield_day": 11, "ongoing": True},
            "STRAWBERRY": {"first_yield_day": 10, "max_yield_day": 16, "ongoing": True},
            "MELON": {"first_yield_day": 10, "max_yield_day": 10, "ongoing": False},
        }

        unplanted = []
        needs_water = []
        needs_harvest = []
        needs_dig = []
        for tx, ty in targets:
            t = me["tiles"][ty][tx]
            if t is None:
                unplanted.append((tx, ty))
            elif isinstance(t, dict):
                if t.get("kind") == "WEED":
                    needs_dig.append((tx, ty))
                elif t.get("kind") == "PLANT":
                    age = day - t["planted_day"]
                    stats = crop_stats.get(t["crop"], {"ongoing": False, "max_yield_day": 10})
                    
                    can_harvest = False
                    if stats["ongoing"]:
                        can_harvest = t.get("yield_units", 0) > 0
                    else:
                        can_harvest = age >= stats["max_yield_day"]
                        
                    if can_harvest:
                        needs_harvest.append((tx, ty))
                    elif not t.get("watered_today"):
                        needs_water.append((tx, ty))
                        
        if needs_dig:
            tx, ty = needs_dig[0]
            if (hx, hy) != (tx, ty):
                if hx < tx: return ["EAST"]
                elif hx > tx: return ["WEST"]
                elif hy < ty: return ["SOUTH"]
                elif hy > ty: return ["NORTH"]
            return ["DIG"]
            
        if needs_harvest:
            tx, ty = needs_harvest[0]
            if (hx, hy) != (tx, ty):
                if hx < tx: return ["EAST"]
                elif hx > tx: return ["WEST"]
                elif hy < ty: return ["SOUTH"]
                elif hy > ty: return ["NORTH"]
            return ["HARVEST"]
            
        if needs_water:
            tx, ty = needs_water[0]
            if (hx, hy) != (tx, ty):
                if hx < tx: return ["EAST"]
                elif hx > tx: return ["WEST"]
                elif hy < ty: return ["SOUTH"]
                elif hy > ty: return ["NORTH"]
            return ["WATER"]
            
        if unplanted and private["seeds"].get(crop, 0) > 0:
            tx, ty = unplanted[0]
            if (hx, hy) != (tx, ty):
                if hx < tx: return ["EAST"]
                elif hx > tx: return ["WEST"]
                elif hy < ty: return ["SOUTH"]
                elif hy > ty: return ["NORTH"]
            return ["PLANT", crop]
            
        if sum(inv.values()) > 0:
            if (hx, hy) != drop_loc:
                if hx < drop_loc[0]: return ["EAST"]
                elif hx > drop_loc[0]: return ["WEST"]
                elif hy < drop_loc[1]: return ["SOUTH"]
                elif hy > drop_loc[1]: return ["NORTH"]
            return ["DROP"]
            
        # Idle near drop loc
        if (hx, hy) != drop_loc:
            if hx < drop_loc[0]: return ["EAST"]
            elif hx > drop_loc[0]: return ["WEST"]
            elif hy < drop_loc[1]: return ["SOUTH"]
            elif hy > drop_loc[1]: return ["NORTH"]
            
        return ["PASS"]

    # Swarm logic
    swarm_tiles = []
    if "SW" in me["unlocked_quadrants"]:
        # SW tiles: x in 0..4, y in 5..9
        for x in range(5):
            for y in range(5, 10):
                if (x, y) not in [(4,4), (4,5), (5,4), (5,5)]:
                    swarm_tiles.append((x, y))
                    
    for i in range(len(me["hands"])):
        if i < 4:
            hx, hy = me["hands"][i]
            hands_actions.append(do_farmer(hx, hy, hand_melon_targets[i], "MELON", i, drop_loc=(4,4)))
        else:
            # Swarm hand
            hx, hy = me["hands"][i]
            # Give each swarm hand a subset of swarm tiles
            subset = swarm_tiles[(i-4)*3 : (i-4)*3 + 3] if swarm_tiles else []
            hands_actions.append(do_farmer(hx, hy, subset, best_crop, i, drop_loc=(4,5)))
            
    # Main farmer is unused, just sit at drop loc
    if (fx, fy) != (4,4):
        farmer = ["EAST"] if fx < 4 else ["WEST"] if fx > 4 else ["SOUTH"] if fy < 4 else ["NORTH"]
    else:
        farmer = ["PASS"]
        
    return {"farmer": farmer, "hands": hands_actions, "market": market[:10]}
