from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS, ANIMALS
import numpy as np
from scipy.optimize import linear_sum_assignment

def agent(obs):
    try:
        player = obs.get("player", 0)
        farms = obs.get("farms", [])
        if not farms:
            return {"farmer": ["PASS"], "hands": [], "market": []}
        my_farm = farms[player]
        private = obs.get("private", {})
        market = obs.get("market", {})
        step = obs.get("step", 0)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        money = my_farm.get("money", 0)
        shed = private.get("shed", {})
        seeds = private.get("seeds", {})
        tiles = my_farm.get("tiles", [])
        board_size = len(tiles)
        unlocked_quads = my_farm.get("unlocked_quadrants", [])
        
        market_actions = []
        field_tasks = [] # (type, loc, prio, kwargs)
        
        # 1. Market Orders: Sell harvested produce
        for prod, qty in shed.items():
            if qty > 0 and prod in ["MILK", "WOOL", "EGG", "FERTILIZER", "WHEAT", "MELON", "STRAWBERRY", "CARROT"]:
                if prod == "WHEAT":
                    # Keep some wheat for feeding animals today & tomorrow
                    animal_count = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("animal"))
                    needed = animal_count * 2
                    surplus = max(0, qty - needed)
                    if surplus > 0:
                        market_actions.append(["SELL", prod, min(10, surplus)])
                else:
                    market_actions.append(["SELL", prod, min(10, qty)])
                    
        # 2. Hiring Strategy: Scale up to 8-10 workers when funds exist
        target_workers = 8 if day >= 2 else (4 if day == 1 else 2)
        hires_today = my_farm.get("hires_today", 0)
        def fib(n):
            return 1 if n <= 1 else fib(n-1) + fib(n-2)
            
        cost_hire = fib(hires_today)
        if hires_today < target_workers and money > cost_hire + 200 and hour < 20:
            market_actions.append(["HIRE"])
            
        # 3. Livestock Infrastructure & Purchases
        # Count current animals & structures
        pastures = []
        coops = []
        cows = 0
        sheep = 0
        geese = 0
        empty_pastures = []
        empty_coops = []
        wheat_count = 0
        empty_tiles = []
        
        for y in range(board_size):
            for x in range(board_size):
                t = tiles[y][x]
                if t is None:
                    empty_tiles.append((x, y))
                elif isinstance(t, dict):
                    kind = t.get("kind")
                    if kind == "PASTURE":
                        pastures.append((x, y))
                        if not t.get("animal"):
                            empty_pastures.append((x, y))
                        else:
                            a = t.get("animal")
                            if a == "COW": cows += 1
                            elif a == "SHEEP": sheep += 1
                    elif kind == "COOP":
                        coops.append((x, y))
                        if not t.get("animal"):
                            empty_coops.append((x, y))
                        else:
                            if t.get("animal") == "GOOSE": geese += 1
                    elif kind == "PLANT":
                        if t.get("crop") == "WHEAT":
                            wheat_count += 1
                            
        # Purchase livestock / seeds if affordable
        if len(empty_pastures) > 0 and cows < 10 and money >= 1500:
            market_actions.append(["BUY_ANIMAL", "COW", 1])
        elif len(empty_pastures) > 0 and sheep < 4 and money >= 1000:
            market_actions.append(["BUY_ANIMAL", "SHEEP", 1])
        elif len(empty_coops) > 0 and geese < 4 and money >= 300:
            market_actions.append(["BUY_ANIMAL", "GOOSE", 1])
            
        # Buy land when empty tiles <= 5
        if len(empty_tiles) <= 5 and (30 - day) >= 10:
            n_unlocked = len(unlocked_quads)
            land_prices = [1000, 2000, 4000]
            if 1 <= n_unlocked <= 3 and money > land_prices[n_unlocked - 1] + 500:
                market_actions.append(["BUY_LAND"])
                
        # Buy Wheat seeds to maintain wheat pipeline
        needed_wheat = max(0, 15 - (wheat_count + seeds.get("WHEAT", 0)))
        if needed_wheat > 0 and money >= needed_wheat * 10 + 100 and hour == 0:
            market_actions.append(["BUY_SEED", "WHEAT", min(8, needed_wheat)])
            
        # 4. Field Tasks:
        # A) Animal Care & Feeding
        for y in range(board_size):
            for x in range(board_size):
                t = tiles[y][x]
                if isinstance(t, dict):
                    if t.get("animal"):
                        # Feed if not fed today and wheat in shed
                        if not t.get("fed_today", True) and shed.get("WHEAT", 0) > 0:
                            field_tasks.append(("FEED", (x, y), 2000, {}))
                        # Harvest animal produce
                        if t.get("yield_units", 0) > 0:
                            field_tasks.append(("HARVEST", (x, y), 1500, {}))
                        # Care for animal
                        if not t.get("cared_today", True):
                            field_tasks.append(("CARE", (x, y), 1200, {}))
                        # Collect fertilizer
                        if t.get("fertilizer_available", False):
                            field_tasks.append(("COLLECT_FERTILIZER", (x, y), 1000, {}))
                    elif t.get("kind") == "PASTURE" and not t.get("animal"):
                        # Place cow or sheep if in shed
                        if shed.get("COW", 0) > 0:
                            field_tasks.append(("PLACE", (x, y), 1800, {"item": "COW"}))
                        elif shed.get("SHEEP", 0) > 0:
                            field_tasks.append(("PLACE", (x, y), 1800, {"item": "SHEEP"}))
                    elif t.get("kind") == "COOP" and not t.get("animal"):
                        if shed.get("GOOSE", 0) > 0:
                            field_tasks.append(("PLACE", (x, y), 1800, {"item": "GOOSE"}))
                    elif t.get("kind") == "PLANT":
                        # Water plant
                        if not t.get("watered_today", True):
                            field_tasks.append(("WATER", (x, y), 1600, {}))
                        # Harvest plant
                        if t.get("yield_units", 0) > 0 and (day - t.get("planted_day", 0) >= CROPS.get(t.get("crop", ""), {}).get("first_yield_day", 999)):
                            field_tasks.append(("HARVEST", (x, y), 1400, {}))
                            
        # B) Build Pastures / Coops on empty tiles
        target_pastures = 8 if day >= 3 else 2
        target_coops = 4 if day >= 5 else 1
        if len(pastures) < target_pastures and money >= 500 and empty_tiles:
            tile = empty_tiles.pop(0)
            field_tasks.append(("BUILD_PASTURE", tile, 1100, {}))
        elif len(coops) < target_coops and money >= 200 and empty_tiles:
            tile = empty_tiles.pop(0)
            field_tasks.append(("BUILD_COOP", tile, 1050, {}))
            
        # C) Plant Wheat on remaining empty tiles
        wheat_seeds = seeds.get("WHEAT", 0)
        while wheat_seeds > 0 and empty_tiles and wheat_count < 20:
            tile = empty_tiles.pop(0)
            field_tasks.append(("PLANT", tile, 900, {"crop": "WHEAT"}))
            wheat_seeds -= 1
            wheat_count += 1
            
        # 5. Worker Assignment with Hungarian Algorithm
        units = [my_farm.get("farmer", [0, 0])] + my_farm.get("hands", [])
        assigned_actions = []
        
        if field_tasks and units:
            n_u = len(units)
            n_t = len(field_tasks)
            cost_mat = np.zeros((n_u, n_t))
            for i, (ux, uy) in enumerate(units):
                for j, (act_type, (tx, ty), prio, kwargs) in enumerate(field_tasks):
                    dist = abs(ux - tx) + abs(uy - ty)
                    cost_mat[i, j] = dist * 10 - prio
            
            row_ind, col_ind = linear_sum_assignment(cost_mat)
            unit_targets = [None] * n_u
            for r, c in zip(row_ind, col_ind):
                unit_targets[r] = field_tasks[c]
                
            for ui, (ux, uy) in enumerate(units):
                target = unit_targets[ui]
                if target is None:
                    assigned_actions.append(["PASS"])
                else:
                    act_type, (tx, ty), prio, kwargs = target
                    if ux == tx and uy == ty:
                        if act_type in ["PLANT", "PLACE"]:
                            item = kwargs.get("crop") or kwargs.get("item")
                            assigned_actions.append([act_type, item])
                        else:
                            assigned_actions.append([act_type])
                    else:
                        # Step toward target
                        if ux > tx: step_act = "WEST"
                        elif ux < tx: step_act = "EAST"
                        elif uy > ty: step_act = "NORTH"
                        elif uy < ty: step_act = "SOUTH"
                        else: step_act = "PASS"
                        assigned_actions.append([step_act])
        else:
            for _ in units:
                assigned_actions.append(["PASS"])
                
        farmer_act = assigned_actions[0] if assigned_actions else ["PASS"]
        hands_act = assigned_actions[1:] if len(assigned_actions) > 1 else []
        
        return {
            "farmer": farmer_act,
            "hands": hands_act,
            "market": market_actions[:10]
        }
    except Exception as e:
        return {"farmer": ["PASS"], "hands": [], "market": []}
