"""
Phase 5: Strawberry Capacity & Initiation Timing Experiment
----------------------------------------------------------
Sweeps strawberry target capacity [20, 25, 30, 35, 40, 45, 50]
and initiation start day [D5, D6, D7, D8, D9].
Measures:
- Final Cash (Mean, Median)
- Win Rate vs V025-A
- Intermediate Cash at Days 8, 12, 18, 24, 29
"""

import os
import sys
import copy
import time
import multiprocessing as mp
import pandas as pd
import numpy as np
from kaggle_environments import make
import importlib.util

_spec = importlib.util.spec_from_file_location("mod_v026_c_base", "agents/v026_c_il_pure_imitation.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
base_agent = _mod.agent

STRAW_CAPACITIES = [20, 25, 30, 35, 40, 45, 50]
START_DAYS = [5, 6, 7, 8, 9]

def create_straw_agent(target_capacity, start_day):
    def parameterized_agent(obs):
        player = obs["player"]
        me = obs["farms"][player]
        day = obs["day"]
        hour = obs["hour"]
        money = me["money"]
        seeds = obs["private"]["seeds"]
        tiles = me["tiles"]
        
        num_strawberries = 0
        empty_unlocked = []
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if t is None: empty_unlocked.append((c, r))
                elif isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                    num_strawberries += 1
                    
        if day > 0 and hour in [1, 6, 12, 18]:
            act = base_agent(obs)
            # Filter existing BUY_SEED STRAWBERRY
            filtered_market = [o for o in act.get("market", []) if not (o[0] == "BUY_SEED" and len(o) > 1 and o[1] == "STRAWBERRY")]
            straw_seeds = seeds.get("STRAWBERRY", 0)
            if day >= start_day and day <= 20 and money >= 250:
                if (num_strawberries + straw_seeds) < target_capacity and len(empty_unlocked) > 3:
                    buy_straw = min(10, target_capacity - (num_strawberries + straw_seeds))
                    filtered_market.append(["BUY_SEED", "STRAWBERRY", buy_straw])
            act["market"] = filtered_market
            return act
        else:
            return base_agent(obs)
            
    return parameterized_agent

def run_straw_match(task):
    cap, s_day, seed, cand_is_p0 = task
    cand_agent = create_straw_agent(cap, s_day)
    
    _spec2 = importlib.util.spec_from_file_location("mod_v025", "agents/v025_a_aggressive_cows.py")
    _mod2 = importlib.util.module_from_spec(_spec2)
    _spec2.loader.exec_module(_mod2)
    v025_agent = _mod2.agent
    
    if cand_is_p0:
        players = [cand_agent, v025_agent]
    else:
        players = [v025_agent, cand_agent]
        
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(players)
    
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    
    cand_score = r0 if cand_is_p0 else r1
    v025_score = r1 if cand_is_p0 else r0
    
    cand_idx = 0 if cand_is_p0 else 1
    
    # Extract intermediate cash at D8, D12, D18, D24, D29
    # Each day is 24 steps
    cash_d8 = env.steps[min(len(env.steps)-1, 8 * 24)][0]["observation"]["farms"][cand_idx]["money"]
    cash_d12 = env.steps[min(len(env.steps)-1, 12 * 24)][0]["observation"]["farms"][cand_idx]["money"]
    cash_d18 = env.steps[min(len(env.steps)-1, 18 * 24)][0]["observation"]["farms"][cand_idx]["money"]
    cash_d24 = env.steps[min(len(env.steps)-1, 24 * 24)][0]["observation"]["farms"][cand_idx]["money"]
    cash_d29 = env.steps[min(len(env.steps)-1, 29 * 24)][0]["observation"]["farms"][cand_idx]["money"]
    
    return {
        "capacity": cap,
        "start_day": s_day,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "v025_score": v025_score,
        "won": 1 if cand_score > v025_score else 0,
        "delta": cand_score - v025_score,
        "cash_d8": cash_d8,
        "cash_d12": cash_d12,
        "cash_d18": cash_d18,
        "cash_d24": cash_d24,
        "cash_d29": cash_d29,
    }

def main():
    print("=== Phase 5: Strawberry Capacity & Initiation Timing Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    
    # Focus sweep: Capacities at default start_day=6, plus cross-sweep of start_days at cap=40
    test_configs = []
    for cap in STRAW_CAPACITIES:
        test_configs.append((cap, 6))
    for s_day in [5, 7, 8, 9]:
        test_configs.append((40, s_day))
        
    tasks = []
    for (cap, s_day) in test_configs:
        for s in SEEDS:
            tasks.append((cap, s_day, s, True))
            tasks.append((cap, s_day, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_straw_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for (cap, s_day), group in df.groupby(["capacity", "start_day"]):
        summary.append({
            "Capacity": cap,
            "Start Day": f"D{s_day}",
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Mean Cash ($)": group["cand_score"].mean(),
            "Median Cash ($)": group["cand_score"].median(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Cash D8 ($)": group["cash_d8"].mean(),
            "Cash D18 ($)": group["cash_d18"].mean(),
            "Cash D29 ($)": group["cash_d29"].mean(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== STRAWBERRY CAPACITY & TIMING SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase5_strawberry_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase5_strawberry_summary.csv", index=False)
    print("\nSaved results to experiments/phase5_strawberry_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
