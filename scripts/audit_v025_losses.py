"""
Comprehensive Loss Audit & Hidden Failure Mode Analysis for V025-A vs V023-G
=============================================================================
Runs seeds 3000..3199 (400 paired games) between V025-A and V023-G.
Analyzes every loss in detail, calculates telemetry, and classifies root cause.
"""

import importlib.util
import json
import multiprocessing as mp
import numpy as np
import os
import pandas as pd
from kaggle_environments import make

AGENT_CACHE = {}

def get_agent_from_path(path):
    if path not in AGENT_CACHE:
        spec = importlib.util.spec_from_file_location("mod_" + os.path.basename(path), path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        AGENT_CACHE[path] = mod.agent
    return AGENT_CACHE[path]

def extract_snapshot(farm, private, day, hour):
    cows, sheep, straw, wheat, melons, carrots = 0, 0, 0, 0, 0, 0
    unwatered_crops = 0
    unfed_animals = 0
    uncared_animals = 0
    fertilizer_avail = 0
    crop_yield_on_tiles = 0
    animal_yield_on_tiles = 0
    
    tiles = farm["tiles"]
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if isinstance(t, dict):
                k = t.get("kind")
                if k in ["PASTURE", "COOP"]:
                    an = t.get("animal")
                    if an == "COW": cows += 1
                    elif an == "SHEEP": sheep += 1
                    if not t.get("fed_today", False): unfed_animals += 1
                    if not t.get("cared_today", False): uncared_animals += 1
                    if t.get("fertilizer_available", False): fertilizer_avail += 1
                    animal_yield_on_tiles += t.get("yield_units", 0)
                elif k == "PLANT":
                    cr = t.get("crop")
                    if cr == "STRAWBERRY": straw += 1
                    elif cr == "WHEAT": wheat += 1
                    elif cr == "MELON": melons += 1
                    elif cr == "CARROT": carrots += 1
                    if not t.get("watered_today", False): unwatered_crops += 1
                    crop_yield_on_tiles += t.get("yield_units", 0)
                    
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])
    carried_wheat = sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
    total_feed = shed.get("WHEAT", 0) + carried_wheat
    
    return {
        "day": day,
        "hour": hour,
        "money": farm["money"],
        "cows": cows,
        "sheep": sheep,
        "straw": straw,
        "wheat": wheat,
        "melons": melons,
        "workers": 1 + len(farm["hands"]),
        "quadrants": len(farm["unlocked_quadrants"]),
        "cows_in_shed": shed.get("COW", 0),
        "straw_seeds": private.get("seeds", {}).get("STRAWBERRY", 0),
        "wheat_seeds": private.get("seeds", {}).get("WHEAT", 0),
        "total_feed": total_feed,
        "shed_milk": shed.get("MILK", 0),
        "shed_wool": shed.get("WOOL", 0),
        "shed_straw": shed.get("STRAWBERRY", 0),
        "shed_fert": shed.get("FERTILIZER", 0),
        "unfed_animals": unfed_animals,
        "uncared_animals": uncared_animals,
        "unwatered_crops": unwatered_crops,
        "crop_yield_on_tiles": crop_yield_on_tiles,
        "animal_yield_on_tiles": animal_yield_on_tiles,
    }

def analyze_single_seed(s):
    v25_agent = get_agent_from_path("agents/v025_a_aggressive_cows.py")
    v23_agent = get_agent_from_path("agents/v023_g_capital_optimizer.py")
    
    results = []
    
    # Position 0 (V025-A as P0, V023-G as P1)
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env0.run([v25_agent, v23_agent])
    
    # Position 1 (V023-G as P0, V025-A as P1)
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([v23_agent, v25_agent])
    
    games = [
        {"pos": "P0", "env": env0, "v25_idx": 0, "v23_idx": 1},
        {"pos": "P1", "env": env1, "v25_idx": 1, "v23_idx": 0},
    ]
    
    for g in games:
        env = g["env"]
        v25_idx = g["v25_idx"]
        v23_idx = g["v23_idx"]
        
        final_v25 = float(env.steps[-1][v25_idx]["reward"])
        final_v23 = float(env.steps[-1][v23_idx]["reward"])
        is_loss = final_v25 < final_v23
        
        day_snapshots_v25 = {}
        day_snapshots_v23 = {}
        
        min_bank_v25 = 999999
        min_bank_v23 = 999999
        
        total_steps = len(env.steps)
        for step_idx in range(total_steps):
            step_state = env.steps[step_idx]
            v25_obs = step_state[v25_idx]["observation"]
            v23_obs = step_state[v23_idx]["observation"]
            
            d = v25_obs["day"]
            h = v25_obs["hour"]
            
            v25_m = v25_obs["farms"][v25_idx]["money"]
            v23_m = v23_obs["farms"][v23_idx]["money"]
            if v25_m < min_bank_v25: min_bank_v25 = v25_m
            if v23_m < min_bank_v23: min_bank_v23 = v23_m
            
            # Record end of day snapshot
            if h == 23 or step_idx == total_steps - 1:
                day_snapshots_v25[d] = extract_snapshot(v25_obs["farms"][v25_idx], v25_obs["private"], d, h)
                day_snapshots_v23[d] = extract_snapshot(v23_obs["farms"][v23_idx], v23_obs["private"], d, h)
                
        # Find first day of significant structural divergence
        first_div_day = -1
        for d in range(30):
            s25 = day_snapshots_v25.get(d)
            s23 = day_snapshots_v23.get(d)
            if s25 and s23:
                if s25["cows"] != s23["cows"] or s25["straw"] != s23["straw"] or abs(s25["money"] - s23["money"]) > 500:
                    first_div_day = d
                    break
                    
        loss_reason = "NONE"
        if is_loss:
            d30_25 = day_snapshots_v25.get(29, {})
            d30_23 = day_snapshots_v23.get(29, {})
            
            d8_25 = day_snapshots_v25.get(8, {})
            d8_23 = day_snapshots_v23.get(8, {})
            
            d15_25 = day_snapshots_v25.get(15, {})
            d15_23 = day_snapshots_v23.get(15, {})
            
            d20_25 = day_snapshots_v25.get(20, {})
            d20_23 = day_snapshots_v23.get(20, {})
            
            # Classification logic
            if d30_25.get("shed_milk", 0) + d30_25.get("shed_wool", 0) > 30 and (final_v23 - final_v25) < 3000:
                loss_reason = "I) final liquidation"
            elif d8_25.get("money", 0) < 50 and d8_25.get("total_feed", 0) < 3:
                loss_reason = "D) feed pressure"
            elif d15_25.get("straw", 0) < d15_23.get("straw", 0) - 15 and d30_23.get("money", 0) > d30_25.get("money", 0):
                loss_reason = "G) insufficient strawberries"
            elif d8_25.get("cows_in_shed", 0) > 1 and d8_25.get("cows", 0) < 4:
                loss_reason = "E) pasture pressure"
            elif d8_25.get("cows", 0) >= 6 and d15_25.get("money", 0) < 2000 and d15_23.get("money", 0) > 8000:
                loss_reason = "C) over-aggressive cow spending"
            elif d30_25.get("quadrants", 1) < d30_23.get("quadrants", 1):
                loss_reason = "H) bad land timing"
            elif abs(d30_25.get("cows", 0) - d30_23.get("cows", 0)) <= 2 and abs(final_v25 - final_v23) < 4000:
                loss_reason = "B) market timing"
            elif d8_25.get("money", 0) < 100 and d8_23.get("money", 0) > 3000:
                loss_reason = "A) cash-flow timing"
            else:
                loss_reason = "J) other"
                
        res = {
            "seed": s,
            "pos": g["pos"],
            "v25_final": final_v25,
            "v23_final": final_v23,
            "delta": final_v25 - final_v23,
            "is_loss": is_loss,
            "loss_reason": loss_reason,
            "first_div_day": first_div_day,
            "gap_d5": day_snapshots_v25.get(5, {}).get("money", 0) - day_snapshots_v23.get(5, {}).get("money", 0),
            "gap_d6": day_snapshots_v25.get(6, {}).get("money", 0) - day_snapshots_v23.get(6, {}).get("money", 0),
            "gap_d8": day_snapshots_v25.get(8, {}).get("money", 0) - day_snapshots_v23.get(8, {}).get("money", 0),
            "gap_d10": day_snapshots_v25.get(10, {}).get("money", 0) - day_snapshots_v23.get(10, {}).get("money", 0),
            "gap_d15": day_snapshots_v25.get(15, {}).get("money", 0) - day_snapshots_v23.get(15, {}).get("money", 0),
            "gap_d20": day_snapshots_v25.get(20, {}).get("money", 0) - day_snapshots_v23.get(20, {}).get("money", 0),
            "gap_d25": day_snapshots_v25.get(25, {}).get("money", 0) - day_snapshots_v23.get(25, {}).get("money", 0),
            "d30_v25_cows": day_snapshots_v25.get(29, {}).get("cows", 0),
            "d30_v25_sheep": day_snapshots_v25.get(29, {}).get("sheep", 0),
            "d30_v25_straw": day_snapshots_v25.get(29, {}).get("straw", 0),
            "d30_v25_wheat": day_snapshots_v25.get(29, {}).get("wheat", 0),
            "d30_v25_workers": day_snapshots_v25.get(29, {}).get("workers", 0),
            "d30_v25_quads": day_snapshots_v25.get(29, {}).get("quadrants", 0),
            "d30_v25_feed": day_snapshots_v25.get(29, {}).get("total_feed", 0),
            "d30_v23_cows": day_snapshots_v23.get(29, {}).get("cows", 0),
            "d30_v23_sheep": day_snapshots_v23.get(29, {}).get("sheep", 0),
            "d30_v23_straw": day_snapshots_v23.get(29, {}).get("straw", 0),
            "d30_v23_wheat": day_snapshots_v23.get(29, {}).get("wheat", 0),
            "d30_v23_workers": day_snapshots_v23.get(29, {}).get("workers", 0),
            "d30_v23_quads": day_snapshots_v23.get(29, {}).get("quadrants", 0),
            "d30_v23_feed": day_snapshots_v23.get(29, {}).get("total_feed", 0),
            "min_bank_v25": min_bank_v25,
            "min_bank_v23": min_bank_v23,
        }
        results.append(res)
        
    return results

def main():
    seeds = list(range(3000, 3200)) # 200 seeds
    pool_size = min(8, mp.cpu_count())
    
    print("=" * 115)
    print("RUNNING IN-DEPTH LOSS AUDIT (Seeds 3000..3199, 400 Games)")
    print("=" * 115)
    
    all_game_results = []
    with mp.Pool(processes=pool_size) as pool:
        for res_list in pool.map(analyze_single_seed, seeds):
            all_game_results.extend(res_list)
            
    df = pd.DataFrame(all_game_results)
    
    total_games = len(df)
    losses = df[df["is_loss"]]
    wins = df[~df["is_loss"]]
    
    print(f"\nTotal Games: {total_games} | Wins: {len(wins)} ({len(wins)/total_games*100:.2f}%) | Losses: {len(losses)} ({len(losses)/total_games*100:.2f}%)")
    print(f"V025-A Mean: ${df['v25_final'].mean():,.0f} | V023-G Mean: ${df['v23_final'].mean():,.0f} | Delta: ${df['delta'].mean():+,.0f}")
    
    print("\n" + "=" * 80)
    print("LOSS BREAKDOWN BY CLASSIFICATION CATEGORY")
    print("=" * 80)
    loss_counts = losses["loss_reason"].value_counts()
    for reason, count in loss_counts.items():
        pct = (count / len(losses)) * 100.0
        pct_total = (count / total_games) * 100.0
        print(f"{reason:<35}: {count:3d} losses ({pct:5.1f}% of losses, {pct_total:4.1f}% of all games)")
        
    os.makedirs("scratch", exist_ok=True)
    df.to_csv("scratch/v025_loss_audit_table.csv", index=False)
    losses.to_csv("scratch/v025_losing_games_only.csv", index=False)
    
    summary_stats = {
        "total_games": total_games,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": float(len(wins)/total_games*100.0),
        "cand_mean": float(df['v25_final'].mean()),
        "opp_mean": float(df['v23_final'].mean()),
        "delta_mean": float(df['delta'].mean()),
        "loss_categories": {k: int(v) for k, v in loss_counts.items()}
    }
    with open("scratch/v025_loss_audit_summary.json", "w") as f:
        json.dump(summary_stats, f, indent=2)
        
    print("\nSaved detailed loss audit to scratch/v025_loss_audit_table.csv and summary to scratch/v025_loss_audit_summary.json")

if __name__ == "__main__":
    mp.freeze_support()
    main()
