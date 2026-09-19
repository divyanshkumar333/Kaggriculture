import sys

def get_target_crop(x, y):
    i = x + y * 10
    if i % 5 == 0: return "MELON"
    if i % 5 == 1: return "STRAWBERRY"
    if i % 5 == 2: return "TOMATO"
    if i % 5 == 3: return "CARROT"
    return "WHEAT"

def agent(obs):
    try:
        player = obs["player"]
        step = obs["step"]
        day = obs["day"]
        farms = obs["farms"]
        me = farms[player]
        private = obs["private"]
        
        market = []
        
        unlocked = me["unlocked_quadrants"]
        if "NE" not in unlocked and me["money"] > 4000:
            market.append(["BUY_LAND"])
        elif "NE" in unlocked and "SW" not in unlocked and me["money"] > 8000:
            market.append(["BUY_LAND"])
        elif "SW" in unlocked and "SE" not in unlocked and me["money"] > 16000:
            market.append(["BUY_LAND"])
            
        num_quads = len(unlocked)
        target_hands = num_quads * 3 
        
        hires_today = me["hires_today"]
        hires_in_market = sum(1 for m in market if m[0] == "HIRE")
        
        if hires_today + hires_in_market < target_hands:
            market.append(["HIRE"])
            
        def is_unlocked(x, y):
            if x < 5 and y < 5: return "NW" in unlocked
            if x >= 5 and y < 5: return "NE" in unlocked
            if x < 5 and y >= 5: return "SW" in unlocked
            if x >= 5 and y >= 5: return "SE" in unlocked
            return False

        crop_stats = {
            "WHEAT": {"max_yield_day": 4, "ongoing": False},
            "CARROT": {"max_yield_day": 3, "ongoing": False},
            "TOMATO": {"max_yield_day": 11, "ongoing": True},
            "STRAWBERRY": {"max_yield_day": 16, "ongoing": True},
            "MELON": {"max_yield_day": 10, "ongoing": False},
        }

        valid_tiles = []
        needed_seeds = {"WHEAT": 0, "CARROT": 0, "TOMATO": 0, "STRAWBERRY": 0, "MELON": 0}
        
        for y in range(10):
            for x in range(10):
                if not is_unlocked(x, y): continue
                if (x, y) in [(4,4), (5,4), (4,5), (5,5)]: continue
                
                valid_tiles.append((x, y))
                t = me["tiles"][y][x]
                if t is None:
                    needed_seeds[get_target_crop(x, y)] += 1
                    
        for crop, needed in needed_seeds.items():
            current_seeds = private["seeds"].get(crop, 0)
            buffer = 2
            total_needed = needed + buffer
            if current_seeds < total_needed:
                buy_amount = total_needed - current_seeds
                if me["money"] > 100:
                    market.append(["BUY_SEED", crop, buy_amount])
                    
        for item, amount in private["shed"].items():
            if amount > 0:
                market.append(["SELL", item, amount])
                
        units = [me["farmer"]] + me["hands"]
        actions = {}
        
        def move_towards(hx, hy, tx, ty):
            if hx < tx: return ["EAST"]
            if hx > tx: return ["WEST"]
            if hy < ty: return ["SOUTH"]
            if hy > ty: return ["NORTH"]
            return ["PASS"]
            
        access_tiles = [(4,4), (5,4), (4,5), (5,5)]
            
        for u_idx, pos in enumerate(units):
            hx, hy = pos
            inv = private["inventories"][u_idx]
            
            if sum(inv.values()) > 0:
                best_access = access_tiles[u_idx % len(access_tiles)]
                if (hx, hy) == best_access:
                    actions[u_idx] = ["DROP"]
                else:
                    actions[u_idx] = move_towards(hx, hy, best_access[0], best_access[1])
                continue
                
            my_tiles = [tile for i, tile in enumerate(valid_tiles) if i % len(units) == u_idx]
            
            my_tasks = []
            for tx, ty in my_tiles:
                t = me["tiles"][ty][tx]
                if t is None:
                    my_tasks.append((3, tx, ty, ["PLANT", get_target_crop(tx, ty)]))
                elif isinstance(t, dict):
                    if t.get("kind") == "WEED":
                        my_tasks.append((4, tx, ty, ["DIG"]))
                    elif t.get("kind") == "PLANT":
                        age = day - t["planted_day"]
                        stats = crop_stats.get(t["crop"], {"ongoing": False, "max_yield_day": 10})
                        
                        can_harvest = False
                        if stats["ongoing"]:
                            y_units = t.get("yield_units", 0)
                            if t["crop"] == "TOMATO":
                                if y_units >= 3 or age >= stats["max_yield_day"] - 1:
                                    can_harvest = y_units > 0
                            elif t["crop"] == "STRAWBERRY":
                                if y_units >= 2 or age >= stats["max_yield_day"] - 1:
                                    can_harvest = y_units > 0
                        else:
                            can_harvest = age >= stats["max_yield_day"]
                            
                        # PRIORITY 1: WATER! (Keep plants alive above all else)
                        if not t.get("watered_today"):
                            my_tasks.append((1, tx, ty, ["WATER"]))
                            
                        # PRIORITY 2: HARVEST!
                        if can_harvest:
                            my_tasks.append((2, tx, ty, ["HARVEST"]))
                            
            if my_tasks:
                best_t = min(my_tasks, key=lambda t: (t[0], abs(hx - t[1]) + abs(hy - t[2])))
                tx, ty = best_t[1], best_t[2]
                if (hx, hy) == (tx, ty):
                    actions[u_idx] = best_t[3]
                else:
                    actions[u_idx] = move_towards(hx, hy, tx, ty)
            else:
                actions[u_idx] = ["PASS"]
                
        market = market[:10]
        hands_actions = [actions.get(i, ["PASS"]) for i in range(1, len(units))]
        return {
            "farmer": actions.get(0, ["PASS"]),
            "hands": hands_actions,
            "market": market
        }
    except Exception as e:
        import traceback, sys
        print(f"AGENT ERROR: {e}", file=sys.__stderr__)
        traceback.print_exc(file=sys.__stderr__)
        return {"farmer": ["PASS"], "hands": [], "market": []}
