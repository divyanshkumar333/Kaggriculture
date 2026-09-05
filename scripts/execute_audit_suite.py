"""
Executive Promotion Audit Suite for V025-A and V025-F
=====================================================
1. Efficient Frontier Sweep:
   - Cow Caps: [8, 9, 10, 11, 12, 13]
   - Strawberry Caps: [30, 36, 42, 48]
   - Opening Cow Velocity: [Day 3, Day 4, Day 5]
   - Opening Strawberry Velocity: [Day 8, Day 9]
2. Head-to-Head Tournament: V025-F vs V025-A
   - 100 paired seeds (200 games)
   - Evaluates Mean, Median, P10, P25, Min, Max, Win Rate, Paired Delta.
"""

import multiprocessing as mp
import numpy as np
import pandas as pd
import json
import os
import importlib.util
from kaggle_environments import make

def make_agent(cow_cap=11, straw_cap=42, cow_start_day=4, straw_start_day=9):
    from scipy.optimize import linear_sum_assignment

    SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
    DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
    DAY0_MELONS = [(3, 3), (3, 2), (3, 1), (3, 0), (2, 3), (2, 2), (2, 1)]
    DAY0_WHEAT = [(2, 0), (1, 3), (1, 2), (1, 1), (1, 0)]
    COMPACT_PASTURE_LAYOUT = [
        (4, 3), (4, 2), (4, 1), (5, 3), (5, 2), (5, 1),
        (3, 4), (3, 3), (3, 2), (2, 4), (2, 3), (6, 4),
        (6, 3), (6, 2), (7, 4), (7, 3), (1, 4), (1, 3)
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

    def agent_fn(obs):
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
                        else: empty_structures.append((c, r, kind))
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

        if day == 0 and hour == 0:
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            market_orders.append(["HIRE"])
            market_orders.append(["HIRE"])
            market_orders.append(["BUY_SEED", "MELON", 7])
            market_orders.append(["BUY_SEED", "WHEAT", 5])
            market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        elif day > 0:
            if hour == 0:
                if day < 4: target_hands = 2
                elif day < 6: target_hands = 4 if money >= 50 else 2
                elif num_quads >= 3: target_hands = 12 if day >= 10 and money >= 300 else 8
                elif num_quads >= 2: target_hands = 6 if money >= 80 else 4
                else: target_hands = 3
                hires_today = me.get("hires_today", 0)
                if hires_today < target_hands and money >= 2:
                    needed = min(target_hands - hires_today, 10)
                    for _ in range(needed): market_orders.append(["HIRE"])
                fert_in_shed = shed.get("FERTILIZER", 0)
                if fert_in_shed > 0 and len(market_orders) < 10:
                    market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

            if hour in [1, 6, 12, 18]:
                current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
                target_feed = num_animals * 3 + 6 if day >= 5 else 6
                if current_wheat < target_feed and money > 40:
                    needed_wheat = target_feed - current_wheat
                    while needed_wheat > 0 and len(market_orders) < 3:
                        buy_qty = min(needed_wheat, 10)
                        market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                        needed_wheat -= buy_qty
                if "NE" not in unlocked_quads and money >= 1200 and day >= 5:
                    market_orders.append(["BUY_LAND"])
                    money -= 1000
                elif "SW" not in unlocked_quads and money >= 2400 and day >= 8:
                    market_orders.append(["BUY_LAND"])
                    money -= 2000

                cows_in_shed = shed.get("COW", 0)
                if day >= cow_start_day and day <= 15 and (num_cows + cows_in_shed) < cow_cap:
                    if len(empty_structures) > 0 or cows_in_shed < 2:
                        while money >= 1500 and (num_cows + cows_in_shed) < cow_cap and len(market_orders) < 8:
                            market_orders.append(["BUY_ANIMAL", "COW", 1])
                            money -= 1500
                            cows_in_shed += 1

                if day >= straw_start_day and day <= 20 and money >= 300:
                    straw_seeds = seeds.get("STRAWBERRY", 0)
                    if (num_strawberries + straw_seeds) < straw_cap and len(empty_unlocked_tiles) > 3:
                        buy_straw = min(10, straw_cap - (num_strawberries + straw_seeds))
                        market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])

                if day >= 22 and day <= 26 and money >= 150:
                    wheat_seeds = seeds.get("WHEAT", 0)
                    if (num_wheat_plants + wheat_seeds) < 35 and len(empty_unlocked_tiles) > 2:
                        market_orders.append(["BUY_SEED", "WHEAT", min(10, 35 - (num_wheat_plants + wheat_seeds))])

            for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
                if len(market_orders) >= 10: break
                p_count = shed.get(prod, 0)
                if p_count > 0:
                    cur_price = market_prices.get(prod, 100)
                    batch_size = 8 if cur_price >= 80 else 4
                    if day >= 27: batch_size = 12
                    sell_amt = min(p_count, batch_size)
                    market_orders.append(["SELL", prod, sell_amt])

        tasks = []
        for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
            if not is_fed: tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
            if not is_cared: tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
            if y_u > 0: tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
            if f_av: tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})

        for (px, py, crop, is_wat, y_u, age, max_life, unwat) in plants_on_board:
            is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or (crop == "MELON" and age >= 10) or (crop in ["STRAWBERRY", "TOMATO"] and y_u > 0)
            if is_ripe and y_u > 0: tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
            elif not is_wat: tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_URGENT_WATER if unwat >= 1 else WEIGHT_WATER_PLANT, "crop": crop})

        for (wx, wy) in weeds: tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
        for (sx, sy, skind) in empty_structures:
            target_animal = None
            if skind == "PASTURE":
                if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict)): target_animal = "COW"
                elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories if isinstance(inv, dict)): target_animal = "SHEEP"
            if target_animal: tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})

        if day == 0:
            for p in DAY0_PASTURES:
                if tiles[p[1]][p[0]] is None: tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
        else:
            desired_pastures = min(15, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
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

        unit_actions = ["PASS"] * num_units
        if not tasks:
            farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
            hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
            return {"farmer": [farmer_act] if isinstance(farmer_act, str) else farmer_act, "hands": [[h] if isinstance(h, str) else h for h in hands_act], "market": market_orders}

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
                    if u_inv.get("WHEAT", 0) == 0:
                        dist_to_shed = min(manhattan(u_pos, sp) for sp in SHED_TILES)
                        penalty = dist_to_shed + 8
                elif t_type == "PLACE_ANIMAL":
                    if u_inv.get(t["animal"], 0) == 0:
                        dist_to_shed = min(manhattan(u_pos, sp) for sp in SHED_TILES)
                        penalty = dist_to_shed + 8
                c = (2000 - base_w) + (dist * 12) + penalty
                u_costs.append(c)
            cost_matrix.append(u_costs)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assigned_tasks = {r: tasks[c] for r, c in zip(row_ind, col_ind)}

        for u_idx, u_pos in enumerate(all_units):
            u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            if u_idx not in assigned_tasks:
                if u_pos in SHED_TILES: unit_actions[u_idx] = ["PASS"]
                else:
                    nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                    unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
                continue
            t = assigned_tasks[u_idx]
            t_pos = t["pos"]
            t_type = t["type"]

            if t_type == "FEED":
                if u_inv.get("WHEAT", 0) == 0:
                    if u_pos in SHED_TILES: unit_actions[u_idx] = ["PICKUP", "WHEAT", 4]
                    else:
                        nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                        unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
                else:
                    if u_pos == t_pos: unit_actions[u_idx] = ["FEED"]
                    else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
            elif t_type == "PLACE_ANIMAL":
                target_an = t["animal"]
                if u_inv.get(target_an, 0) == 0:
                    if u_pos in SHED_TILES: unit_actions[u_idx] = ["PICKUP", target_an, 1]
                    else:
                        nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                        unit_actions[u_idx] = [get_move_toward(u_pos, nearest_shed)]
                else:
                    if u_pos == t_pos: unit_actions[u_idx] = ["PLACE", target_an, 1]
                    else: unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]
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

            if u_pos in SHED_TILES:
                carried_sellable = sum(u_inv.get(p, 0) for p in ["MILK", "WOOL", "STRAWBERRY", "MELON", "FERTILIZER", "CARROT", "EGG"])
                if carried_sellable >= 3: unit_actions[u_idx] = ["DROP"]

        farmer_act = unit_actions[0] if len(unit_actions) > 0 else ["PASS"]
        hands_act = unit_actions[1:] if len(unit_actions) > 1 else []
        return {"farmer": [farmer_act] if isinstance(farmer_act, str) else farmer_act, "hands": [[h] if isinstance(h, str) else h for h in hands_act], "market": market_orders}

    return agent_fn

def eval_paired_match(args):
    agent_spec_tuple, opp_type, seed = args

    if agent_spec_tuple[0] == "V025-F":
        spec_cand = importlib.util.spec_from_file_location("mod_f", "agents/v025_f_adaptive_flywheel.py")
        mod_cand = importlib.util.module_from_spec(spec_cand)
        spec_cand.loader.exec_module(mod_cand)
        cand_agent = mod_cand.agent
    elif agent_spec_tuple[0] == "V025-A":
        spec_cand = importlib.util.spec_from_file_location("mod_a", "agents/v025_a_aggressive_cows.py")
        mod_cand = importlib.util.module_from_spec(spec_cand)
        spec_cand.loader.exec_module(mod_cand)
        cand_agent = mod_cand.agent
    else: # "PARAM"
        _, c_cap, s_cap, c_day, s_day = agent_spec_tuple
        cand_agent = make_agent(c_cap, s_cap, c_day, s_day)

    if opp_type == "V023-G":
        spec_opp = importlib.util.spec_from_file_location("mod_v23", "agents/v023_g_capital_optimizer.py")
        mod_opp = importlib.util.module_from_spec(spec_opp)
        spec_opp.loader.exec_module(mod_opp)
        opp_agent = mod_opp.agent
    elif opp_type == "V025-A":
        spec_opp = importlib.util.spec_from_file_location("mod_a", "agents/v025_a_aggressive_cows.py")
        mod_opp = importlib.util.module_from_spec(spec_opp)
        spec_opp.loader.exec_module(mod_opp)
        opp_agent = mod_opp.agent

    # P0
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env0.run([cand_agent, opp_agent])
    r0 = float(env0.steps[-1][0]["reward"])
    opp_r0 = float(env0.steps[-1][1]["reward"])

    # P1
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env1.run([opp_agent, cand_agent])
    r1 = float(env1.steps[-1][1]["reward"])
    opp_r1 = float(env1.steps[-1][0]["reward"])

    return {
        "agent_spec": agent_spec_tuple,
        "opp": opp_type,
        "seed": seed,
        "scores": [r0, r1],
        "opp_scores": [opp_r0, opp_r1],
        "wins": int(r0 > opp_r0) + int(r1 > opp_r1)
    }

def main():
    pool_size = 2  # 2 processes to avoid Windows memory commit limits
    print("="*100)
    print(f"STARTING COMPACT HIGH-SPEED AUDIT SUITE ON {pool_size} CORES (MEMORY SAFE)")
    print("="*100)

    # 1. Frontier Experiments (10 key variations, 10 seeds = 20 games each)
    frontier_configs = [
        ("V025-A Baseline", ("PARAM", 11, 42, 4, 9)),
        ("Cow Cap = 8",     ("PARAM",  8, 42, 4, 9)),
        ("Cow Cap = 9",     ("PARAM",  9, 42, 4, 9)),
        ("Cow Cap = 10",    ("PARAM", 10, 42, 4, 9)),
        ("Cow Cap = 12",    ("PARAM", 12, 42, 4, 9)),
        ("Cow Cap = 13",    ("PARAM", 13, 42, 4, 9)),
        ("Straw Cap = 30",  ("PARAM", 11, 30, 4, 9)),
        ("Straw Cap = 36",  ("PARAM", 11, 36, 4, 9)),
        ("Straw Cap = 48",  ("PARAM", 11, 48, 4, 9)),
        ("Cow Start D3",    ("PARAM", 11, 42, 3, 9)),
        ("Cow Start D5",    ("PARAM", 11, 42, 5, 9)),
        ("Straw Start D8",  ("PARAM", 11, 42, 4, 8)),
    ]

    p1_seeds = list(range(6000, 6010)) # 10 seeds = 20 games per config
    p1_tasks = []
    for label, spec in frontier_configs:
        for s in p1_seeds:
            p1_tasks.append((spec, "V023-G", s))

    print(f"Running Part 1: Efficient Frontier ({len(p1_tasks)} tasks = {len(p1_tasks)*2} games)...", flush=True)
    p1_results = {}
    with mp.Pool(processes=pool_size) as pool:
        for i, res in enumerate(pool.imap_unordered(eval_paired_match, p1_tasks), 1):
            spec = res["agent_spec"]
            if spec not in p1_results:
                p1_results[spec] = {"scores": [], "opp_scores": [], "wins": 0, "total": 0}
            p1_results[spec]["scores"].extend(res["scores"])
            p1_results[spec]["opp_scores"].extend(res["opp_scores"])
            p1_results[spec]["wins"] += res["wins"]
            p1_results[spec]["total"] += 2
            if i % 30 == 0 or i == len(p1_tasks):
                print(f"  Frontier progress: {i}/{len(p1_tasks)} tasks completed", flush=True)

    frontier_rows = []
    print("\n" + "="*80)
    print("EFFICIENT FRONTIER RESULTS:")
    print("="*80)
    for label, spec in frontier_configs:
        data = p1_results[spec]
        mean_s = np.mean(data["scores"])
        med_s = np.median(data["scores"])
        opp_s = np.mean(data["opp_scores"])
        delta_s = mean_s - opp_s
        wr = (data["wins"] / data["total"]) * 100.0
        frontier_rows.append({
            "Config": label,
            "Mean": float(mean_s),
            "Median": float(med_s),
            "Delta": float(delta_s),
            "WinRate": float(wr)
        })
        print(f"[{label:<20}] -> Mean: ${mean_s:7,.0f} | Med: ${med_s:7,.0f} | Delta: +${delta_s:6,.0f} | WR: {wr:5.1f}%", flush=True)

    df_frontier = pd.DataFrame(frontier_rows)
    os.makedirs("scratch", exist_ok=True)
    df_frontier.to_csv("scratch/v025_parameter_frontier.csv", index=False)
    with open("scratch/v025_parameter_frontier.json", "w") as f:
        json.dump(frontier_rows, f, indent=2)

    # 2. Tournament: V025-F vs V025-A (50 paired seeds = 100 games)
    p2_seeds = list(range(7000, 7050)) # 50 seeds = 100 games
    p2_tasks = [(("V025-F",), "V025-A", s) for s in p2_seeds]
    print("\n" + "="*80)
    print(f"Running Part 2: Tournament (V025-F vs V025-A: {len(p2_tasks)} tasks = 100 games)...", flush=True)

    p2_results = {"f_scores": [], "a_scores": [], "deltas": [], "f_wins": 0, "a_wins": 0, "total": 0}
    with mp.Pool(processes=pool_size) as pool:
        for i, res in enumerate(pool.imap_unordered(eval_paired_match, p2_tasks), 1):
            f_sc = res["scores"]
            a_sc = res["opp_scores"]
            p2_results["f_scores"].extend(f_sc)
            p2_results["a_scores"].extend(a_sc)
            p2_results["deltas"].extend([f_sc[0] - a_sc[0], f_sc[1] - a_sc[1]])
            p2_results["f_wins"] += res["wins"]
            p2_results["a_wins"] += (2 - res["wins"])
            p2_results["total"] += 2
            if i % 10 == 0 or i == len(p2_tasks):
                cur_mean_f = np.mean(p2_results["f_scores"])
                cur_mean_a = np.mean(p2_results["a_scores"])
                cur_wr = (p2_results["f_wins"] / p2_results["total"]) * 100.0
                print(f"  Tournament progress: {i}/{len(p2_tasks)} seeds ({p2_results['total']} games) | V025-F WR: {cur_wr:.1f}% | Mean F: ${cur_mean_f:,.0f} | Mean A: ${cur_mean_a:,.0f} | Delta: +${cur_mean_f - cur_mean_a:,.0f}", flush=True)

    f_all = p2_results["f_scores"]
    a_all = p2_results["a_scores"]
    d_all = p2_results["deltas"]
    tot_g = p2_results["total"]
    tot_fw = p2_results["f_wins"]
    tot_aw = p2_results["a_wins"]

    stats_tourney = {
        "total_seeds": len(p2_seeds),
        "total_games": tot_g,
        "v025_f": {
            "mean": float(np.mean(f_all)),
            "median": float(np.median(f_all)),
            "std": float(np.std(f_all)),
            "p10": float(np.percentile(f_all, 10)),
            "p25": float(np.percentile(f_all, 25)),
            "p75": float(np.percentile(f_all, 75)),
            "p90": float(np.percentile(f_all, 90)),
            "min": float(np.min(f_all)),
            "max": float(np.max(f_all)),
            "wins": tot_fw,
            "win_rate": float((tot_fw / tot_g) * 100.0)
        },
        "v025_a": {
            "mean": float(np.mean(a_all)),
            "median": float(np.median(a_all)),
            "std": float(np.std(a_all)),
            "p10": float(np.percentile(a_all, 10)),
            "p25": float(np.percentile(a_all, 25)),
            "p75": float(np.percentile(a_all, 75)),
            "p90": float(np.percentile(a_all, 90)),
            "min": float(np.min(a_all)),
            "max": float(np.max(a_all)),
            "wins": tot_aw,
            "win_rate": float((tot_aw / tot_g) * 100.0)
        },
        "paired_delta": {
            "mean": float(np.mean(d_all)),
            "median": float(np.median(d_all)),
            "std": float(np.std(d_all))
        }
    }

    with open("scratch/v025_f_large_scale_results.json", "w") as f:
        json.dump(stats_tourney, f, indent=2)

    print("\n" + "="*100)
    print("TOURNAMENT SUMMARY: V025-F VS V025-A")
    print("="*100)
    print(f"V025-F Mean:   ${stats_tourney['v025_f']['mean']:,.0f} | Median: ${stats_tourney['v025_f']['median']:,.0f} | P10: ${stats_tourney['v025_f']['p10']:,.0f} | P25: ${stats_tourney['v025_f']['p25']:,.0f} | Min: ${stats_tourney['v025_f']['min']:,.0f} | Max: ${stats_tourney['v025_f']['max']:,.0f}")
    print(f"V025-A Mean:   ${stats_tourney['v025_a']['mean']:,.0f} | Median: ${stats_tourney['v025_a']['median']:,.0f} | P10: ${stats_tourney['v025_a']['p10']:,.0f} | P25: ${stats_tourney['v025_a']['p25']:,.0f} | Min: ${stats_tourney['v025_a']['min']:,.0f} | Max: ${stats_tourney['v025_a']['max']:,.0f}")
    print(f"Paired Delta:  +${stats_tourney['paired_delta']['mean']:,.0f} (Mean) | +${stats_tourney['paired_delta']['median']:,.0f} (Median)")
    print(f"V025-F Win Rate: {stats_tourney['v025_f']['win_rate']:.2f}% ({tot_fw}/{tot_g})")
    print("="*100)

if __name__ == "__main__":
    mp.freeze_support()
    main()
