"""
Phase 4: Cow Capacity Saturation Curve Experiment
-------------------------------------------------
Sweeps maximum cow target across [0, 2, 4, 6, 8, 9, 10, 11, 12].
Measures:
- Final Cash (Mean, Median)
- Win Rate vs V025-A
- Milk Volume Produced
- Milk Market Price Trajectory (D10, D20, D30)
- Opportunity cost / cash generation efficiency
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

COW_TARGETS = [0, 2, 4, 6, 8, 9, 10, 11, 12]

def create_cow_agent(target_cows):
    def parameterized_agent(obs):
        player = obs["player"]
        me = obs["farms"][player]
        day = obs["day"]
        hour = obs["hour"]
        money = me["money"]
        shed = obs["private"]["shed"]
        tiles = me["tiles"]
        
        # Count existing cows
        num_cows = 0
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if isinstance(t, dict) and t.get("kind") in ["COOP", "PASTURE"] and t.get("animal") == "COW":
                    num_cows += 1
                    
        # Intercept Day 0 cows if target_cows < 2
        if day == 0 and hour == 0:
            act = base_agent(obs)
            m_orders = []
            m_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            for _ in range(5):
                m_orders.append(["HIRE"])
            d0_cows = min(2, target_cows)
            if d0_cows > 0:
                m_orders.append(["BUY_ANIMAL", "COW", d0_cows])
            m_orders.append(["BUY_ANIMAL", "SHEEP", 2])
            m_orders.append(["BUY_SEED", "MELON", 11])
            m_orders.append(["BUY_SEED", "WHEAT", 5])
            m_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            act["market"] = m_orders
            return act
        elif day > 0 and hour in [1, 6, 12, 18]:
            act = base_agent(obs)
            # Filter existing BUY_ANIMAL COW orders
            filtered_market = [o for o in act.get("market", []) if not (o[0] == "BUY_ANIMAL" and len(o) > 1 and o[1] == "COW")]
            cows_in_shed = shed.get("COW", 0)
            if day >= 3 and day <= 15 and (num_cows + cows_in_shed) < target_cows:
                curr_money = money
                while curr_money >= 500 and (num_cows + cows_in_shed) < target_cows and len(filtered_market) < 8:
                    filtered_market.append(["BUY_ANIMAL", "COW", 1])
                    curr_money -= 400
                    cows_in_shed += 1
            act["market"] = filtered_market
            return act
        else:
            return base_agent(obs)
            
    return parameterized_agent

def run_cow_match(task):
    target_cows, seed, cand_is_p0 = task
    cand_agent = create_cow_agent(target_cows)
    
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
    
    # Track final milk price
    final_obs = env.steps[-1][0]["observation"]
    milk_price_final = final_obs.get("market", {}).get("prices", {}).get("MILK", 0)
    
    return {
        "target_cows": target_cows,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "v025_score": v025_score,
        "won": 1 if cand_score > v025_score else 0,
        "delta": cand_score - v025_score,
        "milk_price_final": milk_price_final,
    }

def main():
    print("=== Phase 4: Cow Capacity Saturation Curve Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    print(f"Sweeping cow targets {COW_TARGETS} across {len(SEEDS)} paired seeds (20 matches per setting)...", flush=True)
    
    tasks = []
    for c in COW_TARGETS:
        for s in SEEDS:
            tasks.append((c, s, True))
            tasks.append((c, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_cow_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for c, group in df.groupby("target_cows"):
        summary.append({
            "Target Cows": c,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Mean Cash ($)": group["cand_score"].mean(),
            "Median Cash ($)": group["cand_score"].median(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Delta Std ($)": group["delta"].std(),
            "Final Milk Price ($)": group["milk_price_final"].mean(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== COW CAPACITY SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase4_cow_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase4_cow_summary.csv", index=False)
    print("\nSaved results to experiments/phase4_cow_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
