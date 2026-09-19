import sys

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
        if "NE" not in unlocked and me["money"] > 3000:
            market.append(["BUY_LAND"])
        elif "NE" in unlocked and "SW" not in unlocked and me["money"] > 6000:
            market.append(["BUY_LAND"])
        elif "SW" in unlocked and "SE" not in unlocked and me["money"] > 10000:
            market.append(["BUY_LAND"])
            
        num_quads = len(unlocked)
        target_hands = min(10, num_quads * 3) 
        
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

        valid_tiles = []
        needed_seeds = 0
        
        for y in range(10):
            for x in range(10):
                if not is_unlocked(x, y): continue
                if (x, y) in [(4,4), (5,4), (4,5), (5,5)]: continue
                
                valid_tiles.append((x, y))
                t = me["tiles"][y][x]
                if t is None:
                    needed_seeds += 1
                    
        def get_quad(x, y):
            if x < 5 and y < 5: return 0
            if x >= 5 and y < 5: return 1
            if x < 5 and y >= 5: return 2
            return 3
            
        valid_tiles.sort(key=lambda p: (get_quad(p[0], p[1]), p[1], p[0]))
                    
        current_seeds = private["seeds"].get("WHEAT", 0)
        buffer = 5
        total_needed = needed_seeds + buffer
        if current_seeds < total_needed:
            buy_amount = total_needed - current_seeds
            if me["money"] > 100:
                market.append(["BUY_SEED", "WHEAT", buy_amount])
                
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
        
        chunk_size = len(valid_tiles) // len(units) if units else 1
            
        for u_idx, pos in enumerate(units):
            hx, hy = pos
            inv = private["inventories"][u_idx]
            
            start_idx = u_idx * chunk_size
            end_idx = start_idx + chunk_size if u_idx < len(units) - 1 else len(valid_tiles)
            my_tiles = valid_tiles[start_idx:end_idx]
            
            my_tasks = []
            for tx, ty in my_tiles:
                t = me["tiles"][ty][tx]
                if t is None:
                    if private["seeds"].get("WHEAT", 0) > 0:
                        my_tasks.append((3, tx, ty, ["PLANT", "WHEAT"]))
                elif isinstance(t, dict):
                    if t.get("kind") == "WEED":
                        my_tasks.append((4, tx, ty, ["DIG"]))
                    elif t.get("kind") == "PLANT":
                        age = day - t["planted_day"]
                        can_harvest = age >= 4
                        
                        if can_harvest:
                            my_tasks.append((0, tx, ty, ["HARVEST"]))
                        elif not t.get("watered_today"):
                            my_tasks.append((1, tx, ty, ["WATER"]))
                            
            if sum(inv.values()) >= 9 or (sum(inv.values()) > 0 and not my_tasks):
                best_access = access_tiles[u_idx % len(access_tiles)]
                if (hx, hy) == best_access:
                    actions[u_idx] = ["DROP"]
                else:
                    actions[u_idx] = move_towards(hx, hy, best_access[0], best_access[1])
                continue
                            
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
