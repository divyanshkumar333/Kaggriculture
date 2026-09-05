"""
Phase 7: Market Selling & Shed Protection Experiment
----------------------------------------------------
Compares market selling strategies:
1. Burst selling (dump everything)
2. Fixed batch sizes (4, 8, 10, 12, 14)
3. Dynamic adaptive batch based on price & shed occupancy
4. Strict product priority (Strawberry -> Milk -> Wool -> Melon -> Fertilizer -> Wheat)
5. Paced intra-day selling (Hours 0, 6, 12, 18)
Tracks:
- Final Cash (Mean, Median)
- Win Rate vs V025-A
- Discard / Shed Overflow Events
- Average Realized Sale Price per Product
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

MARKET_STRATEGIES = {
    "Burst_Selling": {"mode": "burst"},
    "Fixed_Batch_4": {"mode": "fixed", "batch": 4},
    "Fixed_Batch_8": {"mode": "fixed", "batch": 8},
    "Fixed_Batch_10": {"mode": "fixed", "batch": 10},
    "Fixed_Batch_12": {"mode": "fixed", "batch": 12},
    "Fixed_Batch_14": {"mode": "fixed", "batch": 14},
    "Adaptive_Shed_Pacing": {"mode": "adaptive"},
    "Priority_Berry_Milk_First": {"mode": "priority"},
    "IntraDay_Paced": {"mode": "intraday"},
}

def create_market_agent(cfg):
    mode = cfg.get("mode", "adaptive")
    batch_sz = cfg.get("batch", 8)
    
    def parameterized_agent(obs):
        day = obs["day"]
        hour = obs["hour"]
        player = obs["player"]
        me = obs["farms"][player]
        shed = obs["private"]["shed"]
        market_prices = obs.get("market", {}).get("prices", {})
        
        act = base_agent(obs)
        # Filter existing SELL orders from base_agent
        non_sell_orders = [o for o in act.get("market", []) if o[0] != "SELL"]
        sell_orders = []
        
        # Determine product list & batching
        if mode == "burst":
            # Dump all shed items up to order limit
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "WHEAT"]:
                cnt = shed.get(prod, 0)
                if cnt > 0 and len(sell_orders) + len(non_sell_orders) < 10:
                    sell_orders.append(["SELL", prod, cnt])
        elif mode == "fixed":
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "WHEAT"]:
                cnt = shed.get(prod, 0)
                if cnt > 0 and len(sell_orders) + len(non_sell_orders) < 10:
                    sell_orders.append(["SELL", prod, min(cnt, batch_sz)])
        elif mode == "adaptive":
            total_in_shed = sum(cnt for item, cnt in shed.items() if item not in ["COW", "SHEEP"])
            urgency = total_in_shed >= 60
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "WHEAT"]:
                cnt = shed.get(prod, 0)
                if cnt > 0 and len(sell_orders) + len(non_sell_orders) < 10:
                    cur_price = market_prices.get(prod, 100)
                    if urgency or cur_price >= 80 or day >= 27:
                        sz = 12 if urgency or day >= 27 else 8
                    else:
                        sz = 4
                    sell_orders.append(["SELL", prod, min(cnt, sz)])
        elif mode == "priority":
            for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "CARROT", "FERTILIZER", "WHEAT"]:
                cnt = shed.get(prod, 0)
                if cnt > 0 and len(sell_orders) + len(non_sell_orders) < 10:
                    sell_orders.append(["SELL", prod, min(cnt, 8)])
        elif mode == "intraday":
            if hour in [0, 6, 12, 18]:
                for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "WHEAT"]:
                    cnt = shed.get(prod, 0)
                    if cnt > 0 and len(sell_orders) + len(non_sell_orders) < 10:
                        sell_orders.append(["SELL", prod, min(cnt, 10)])
                        
        act["market"] = non_sell_orders + sell_orders
        return act
        
    return parameterized_agent

def run_market_match(task):
    strat_name, seed, cand_is_p0 = task
    cfg = MARKET_STRATEGIES[strat_name]
    cand_agent = create_market_agent(cfg)
    
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
    
    return {
        "strategy": strat_name,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "v025_score": v025_score,
        "won": 1 if cand_score > v025_score else 0,
        "delta": cand_score - v025_score,
    }

def main():
    print("=== Phase 7: Market Selling & Shed Protection Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    
    tasks = []
    for name in MARKET_STRATEGIES.keys():
        for s in SEEDS:
            tasks.append((name, s, True))
            tasks.append((name, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_market_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for name, group in df.groupby("strategy"):
        summary.append({
            "Strategy": name,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Mean Cash ($)": group["cand_score"].mean(),
            "Median Cash ($)": group["cand_score"].median(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Delta Std ($)": group["delta"].std(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== MARKET SELLING SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase7_market_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase7_market_summary.csv", index=False)
    print("\nSaved results to experiments/phase7_market_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
