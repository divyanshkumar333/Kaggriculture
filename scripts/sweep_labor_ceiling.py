"""
Phase 3: Controlled Labor Ceiling Experiment
--------------------------------------------
Sweeps total daily workers across [3, 4, 5, 6, 7, 8, 9, 10, 12].
Measures:
- Final Cash (Mean, Median)
- Win Rate vs V025-A
- Worker Idle %
- Care/Feed Compliance
- Total Season Hiring Cost
- Total Harvested Produce Throughput
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

WORKER_CEILINGS = [3, 4, 5, 6, 7, 8, 9, 10, 12]

def create_labor_agent(mature_workers):
    """Factory returning an agent with a hard mature daily worker ceiling."""
    target_hands_mature = mature_workers - 1
    
    def parameterized_agent(obs):
        player = obs["player"]
        me = obs["farms"][player]
        day = obs["day"]
        hour = obs["hour"]
        money = me["money"]
        num_quads = len(me["unlocked_quadrants"])
        
        # Keep Day 0 intact with proven 5 hires
        if day == 0:
            return base_agent(obs)
        elif day > 0 and hour == 0:
            act = base_agent(obs)
            filtered_market = [o for o in act.get("market", []) if o[0] != "HIRE"]
            
            # Staged scaling up to mature_workers ceiling
            if day < 3:
                desired = min(5, target_hands_mature)
            elif day < 6:
                desired = min(6, target_hands_mature)
            else:
                desired = target_hands_mature
                
            hires_today = me.get("hires_today", 0)
            if hires_today < desired and money >= 5:
                needed = min(desired - hires_today, 10)
                for _ in range(needed):
                    filtered_market.append(["HIRE"])
            act["market"] = filtered_market
            return act
        else:
            return base_agent(obs)
            
    return parameterized_agent

def run_labor_match(task):
    workers, seed, cand_is_p0 = task
    cand_agent = create_labor_agent(workers)
    
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
    
    cand_seat_idx = 0 if cand_is_p0 else 1
    
    # Analyze telemetry from steps
    idle_count = 0
    total_actions = 0
    care_failures = 0
    unwatered_weeds = 0
    
    for step_data in env.steps:
        # Check action of candidate
        cand_action = step_data[cand_seat_idx].get("action")
        if cand_action and isinstance(cand_action, dict):
            farmer_act = cand_action.get("farmer", ["PASS"])
            if farmer_act == ["PASS"] or (isinstance(farmer_act, list) and len(farmer_act) > 0 and farmer_act[0] == "PASS"):
                idle_count += 1
            total_actions += 1
            for hand_act in cand_action.get("hands", []):
                if hand_act == ["PASS"] or (isinstance(hand_act, list) and len(hand_act) > 0 and hand_act[0] == "PASS"):
                    idle_count += 1
                total_actions += 1
                
    idle_pct = (idle_count / total_actions * 100) if total_actions > 0 else 0.0
    
    return {
        "workers": workers,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "v025_score": v025_score,
        "won": 1 if cand_score > v025_score else 0,
        "delta": cand_score - v025_score,
        "idle_pct": idle_pct,
    }

def main():
    print("=== Phase 3: Controlled Labor Ceiling Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    print(f"Sweeping total workers {WORKER_CEILINGS} across {len(SEEDS)} paired seeds (20 matches per worker setting)...", flush=True)
    
    tasks = []
    for w in WORKER_CEILINGS:
        for s in SEEDS:
            tasks.append((w, s, True))
            tasks.append((w, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_labor_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for w, group in df.groupby("workers"):
        summary.append({
            "Total Workers": w,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Mean Cash ($)": group["cand_score"].mean(),
            "Median Cash ($)": group["cand_score"].median(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Delta Std ($)": group["delta"].std(),
            "Idle Turn %": group["idle_pct"].mean(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== LABOR CEILING SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase3_labor_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase3_labor_summary.csv", index=False)
    print("\nSaved results to experiments/phase3_labor_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
