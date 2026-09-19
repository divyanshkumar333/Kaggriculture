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
        target_hands = min(12, num_quads * 4)  # Boost hands since they never drop
        
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
        
        tasks_by_prio = {0: [], 1: [], 3: [], 4: []}
        for tx, ty in valid_tiles:
            t = me["tiles"][ty][tx]
            if t is None:
                if private["seeds"].get("WHEAT", 0) > 0:
                    tasks_by_prio[3].append((tx, ty, ["PLANT", "WHEAT"]))
            elif isinstance(t, dict):
                if t.get("kind") == "WEED":
                    tasks_by_prio[4].append((tx, ty, ["DIG"]))
                elif t.get("kind") == "PLANT":
                    age = day - t["planted_day"]
                    if age >= 4:
                        tasks_by_prio[0].append((tx, ty, ["HARVEST"]))
                    elif not t.get("watered_today"):
                        tasks_by_prio[1].append((tx, ty, ["WATER"]))
                        
        available_units = list(range(len(units)))
        
        for prio in [0, 1, 3, 4]:
            prio_tasks = tasks_by_prio[prio]
            while prio_tasks and available_units:
                best_pair = None
                best_dist = 9999
                
                for u_idx in available_units:
                    hx, hy = units[u_idx]
                    for t_idx, (tx, ty, act) in enumerate(prio_tasks):
                        dist = abs(hx - tx) + abs(hy - ty)
                        if dist < best_dist:
                            best_dist = dist
                            best_pair = (u_idx, t_idx)
                            
                u_idx, t_idx = best_pair
                tx, ty, act = prio_tasks[t_idx]
                
                hx, hy = units[u_idx]
                if (hx, hy) == (tx, ty):
                    actions[u_idx] = act
                else:
                    actions[u_idx] = move_towards(hx, hy, tx, ty)
                    
                available_units.remove(u_idx)
                prio_tasks.pop(t_idx)
                
        # If units have nothing to do, THEN they drop
        for u_idx in available_units:
            inv = private["inventories"][u_idx]
            if sum(inv.values()) > 0:
                pos = units[u_idx]
                best_access = access_tiles[u_idx % len(access_tiles)]
                if pos[0] == best_access[0] and pos[1] == best_access[1]:
                    actions[u_idx] = ["DROP"]
                else:
                    actions[u_idx] = move_towards(pos[0], pos[1], best_access[0], best_access[1])
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
