"""
Phase 6: Crop Succession Experiment
-----------------------------------
Compares strawberry liquidation and wheat succession schedules:
1. No succession (control)
2. Destroy on D21, D22, D23, D24, D25
3. Progressive partial succession (replacing exhausted plants)
4. Grandmaster replay schedule (staggered liquidation D23-D25)
Replacement wheat counts: [20, 25, 30, 35, 40, 45].
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

SUCCESSION_CONFIGS = {
    "No_Succession": {"mode": "none"},
    "Destroy_D21": {"mode": "day", "day": 21, "wheat": 35},
    "Destroy_D22": {"mode": "day", "day": 22, "wheat": 35},
    "Destroy_D23": {"mode": "day", "day": 23, "wheat": 35},
    "Destroy_D24": {"mode": "day", "day": 24, "wheat": 35},
    "Destroy_D25": {"mode": "day", "day": 25, "wheat": 35},
    "Progressive_Partial": {"mode": "progressive", "wheat": 35},
    "GM_Staggered_D23_25": {"mode": "staggered", "wheat": 35},
    "Wheat_Count_20": {"mode": "day", "day": 23, "wheat": 20},
    "Wheat_Count_25": {"mode": "day", "day": 23, "wheat": 25},
    "Wheat_Count_30": {"mode": "day", "day": 23, "wheat": 30},
    "Wheat_Count_40": {"mode": "day", "day": 23, "wheat": 40},
    "Wheat_Count_45": {"mode": "day", "day": 23, "wheat": 45},
}

def create_succession_agent(cfg):
    mode = cfg.get("mode", "none")
    cut_day = cfg.get("day", 23)
    wheat_count = cfg.get("wheat", 35)
    
    def parameterized_agent(obs):
        day = obs["day"]
        hour = obs["hour"]
        player = obs["player"]
        me = obs["farms"][player]
        money = me["money"]
        seeds = obs["private"]["seeds"]
        tiles = me["tiles"]
        
        # Intercept strawberry liquidation and wheat buying
        act = base_agent(obs)
        market_orders = act.get("market", [])
        
        # Determine whether to buy replacement wheat seeds
        if mode != "none" and day in [21, 22, 23, 24] and hour == 0:
            wheat_seeds = seeds.get("WHEAT", 0)
            if wheat_seeds < wheat_count and money >= 20:
                buy_amt = min(10, wheat_count - wheat_seeds)
                if len(market_orders) < 10:
                    market_orders.append(["BUY_SEED", "WHEAT", buy_amt])
                    
        # DIG tasks for succession
        # If we are in succession mode, inject DIG tasks for strawberries
        dig_positions = []
        if mode == "day" and day >= cut_day:
            for r in range(10):
                for c in range(10):
                    t = tiles[r][c]
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                        dig_positions.append((c, r))
        elif mode == "progressive" and day >= 22:
            for r in range(10):
                for c in range(10):
                    t = tiles[r][c]
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                        # If plant is old or yield is 0
                        if day - t.get("planted_day", day) >= 15 or t.get("yield_units", 0) == 0:
                            dig_positions.append((c, r))
        elif mode == "staggered":
            max_dig = 12 if day == 23 else (24 if day == 24 else (40 if day >= 25 else 0))
            if max_dig > 0:
                count = 0
                for r in range(10):
                    for c in range(10):
                        t = tiles[r][c]
                        if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                            if count < max_dig:
                                dig_positions.append((c, r))
                                count += 1
                                
        # Check if farmer can dig
        if dig_positions and hour < 20:
            # If farmer is standing on one of the dig positions, DIG!
            fx, fy = me["farmer"]
            if (fx, fy) in dig_positions:
                act["farmer"] = ["DIG"]
            for i, h in enumerate(me["hands"]):
                hx, hy = h
                if (hx, hy) in dig_positions and i < len(act.get("hands", [])):
                    act["hands"][i] = ["DIG"]
                    
        act["market"] = market_orders
        return act
        
    return parameterized_agent

def run_succession_match(task):
    cfg_name, seed, cand_is_p0 = task
    cfg = SUCCESSION_CONFIGS[cfg_name]
    cand_agent = create_succession_agent(cfg)
    
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
        "config": cfg_name,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "v025_score": v025_score,
        "won": 1 if cand_score > v025_score else 0,
        "delta": cand_score - v025_score,
    }

def main():
    print("=== Phase 6: Crop Succession Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    
    tasks = []
    for name in SUCCESSION_CONFIGS.keys():
        for s in SEEDS:
            tasks.append((name, s, True))
            tasks.append((name, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_succession_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for name, group in df.groupby("config"):
        summary.append({
            "Configuration": name,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Mean Cash ($)": group["cand_score"].mean(),
            "Median Cash ($)": group["cand_score"].median(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Delta Std ($)": group["delta"].std(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== CROP SUCCESSION SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase6_succession_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase6_succession_summary.csv", index=False)
    print("\nSaved results to experiments/phase6_succession_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
