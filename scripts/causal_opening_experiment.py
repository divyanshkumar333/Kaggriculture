"""
Phase 2: Grandmaster Opening Controlled Experiment
--------------------------------------------------
Compares Day-0 opening configurations under strictly identical seeds and mirror play.
Tests:
- V025-A baseline (4 Sheep, 0 Cows, 7 Melons, 5 Wheat, 2 Hires)
- V026 baseline
- GM Opening (2 Cows, 2 Sheep, 11 Melons, 5 Wheat, 5 Hires)
- Single-variable counterfactual variations:
  * 1 Cow vs 2 Cows vs 3 Cows
  * 1 Sheep vs 2 Sheep
  * 9 vs 10 vs 11 vs 12 vs 13 Melons
  * 4 vs 5 vs 6 Hires
  * 3 vs 5 vs 7 Wheat
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

def create_opening_agent(cows=2, sheep=2, melons=11, wheat=5, hires=5):
    """Factory returning an agent with parameterized Day-0 opening."""
    def parameterized_agent(obs):
        # Override opening on Day 0, hour 0
        player = obs["player"]
        me = obs["farms"][player]
        day = obs["day"]
        hour = obs["hour"]
        
        if day == 0 and hour == 0:
            # Custom parameterized opening market orders
            market_orders = []
            # Feed buffer
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            for _ in range(hires):
                market_orders.append(["HIRE"])
            if cows > 0:
                market_orders.append(["BUY_ANIMAL", "COW", cows])
            if sheep > 0:
                market_orders.append(["BUY_ANIMAL", "SHEEP", sheep])
            if melons > 0:
                market_orders.append(["BUY_SEED", "MELON", melons])
            if wheat > 0:
                market_orders.append(["BUY_SEED", "WHEAT", wheat])
            market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
            
            # Let base agent handle task dispatch for day 0
            action_dict = base_agent(obs)
            action_dict["market"] = market_orders
            return action_dict
        else:
            return base_agent(obs)
            
    return parameterized_agent

# Global dictionary of variants for multiprocessing workers
VARIANT_CONFIGS = {
    "V025_A_Baseline": "agents/v025_a_aggressive_cows.py",
    "Current_V026": "agents/v026_c_il_pure_imitation.py",
    "GM_Opening": {"cows": 2, "sheep": 2, "melons": 11, "wheat": 5, "hires": 5},
    "GM_1Cow": {"cows": 1, "sheep": 2, "melons": 11, "wheat": 5, "hires": 5},
    "GM_3Cows": {"cows": 3, "sheep": 2, "melons": 8, "wheat": 5, "hires": 5}, # adjusted melons for budget
    "GM_1Sheep": {"cows": 2, "sheep": 1, "melons": 11, "wheat": 5, "hires": 5},
    "GM_9Melons": {"cows": 2, "sheep": 2, "melons": 9, "wheat": 5, "hires": 5},
    "GM_10Melons": {"cows": 2, "sheep": 2, "melons": 10, "wheat": 5, "hires": 5},
    "GM_12Melons": {"cows": 2, "sheep": 2, "melons": 12, "wheat": 5, "hires": 5},
    "GM_13Melons": {"cows": 2, "sheep": 2, "melons": 13, "wheat": 3, "hires": 5},
    "GM_4Hires": {"cows": 2, "sheep": 2, "melons": 11, "wheat": 5, "hires": 4},
    "GM_6Hires": {"cows": 2, "sheep": 2, "melons": 11, "wheat": 5, "hires": 6},
    "GM_3Wheat": {"cows": 2, "sheep": 2, "melons": 11, "wheat": 3, "hires": 5},
    "GM_7Wheat": {"cows": 2, "sheep": 2, "melons": 11, "wheat": 7, "hires": 5},
}

def run_match(task):
    variant_name, seed, cand_is_p0 = task
    cfg = VARIANT_CONFIGS[variant_name]
    
    # Load candidate agent
    if isinstance(cfg, str):
        import importlib.util
        spec = importlib.util.spec_from_file_location("mod_cand", cfg)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cand_agent = m.agent
    else:
        cand_agent = create_opening_agent(**cfg)
        
    # Load opponent (V025-A)
    import importlib.util
    spec2 = importlib.util.spec_from_file_location("mod_v025", "agents/v025_a_aggressive_cows.py")
    m2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(m2)
    v025_agent = m2.agent
    
    if cand_is_p0:
        players = [cand_agent, v025_agent]
    else:
        players = [v025_agent, cand_agent]
        
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(players)
    
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    
    if cand_is_p0:
        s_cand, s_v025 = r0, r1
    else:
        s_cand, s_v025 = r1, r0
        
    return {
        "variant": variant_name,
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": s_cand,
        "v025_score": s_v025,
        "won": 1 if s_cand > s_v025 else 0,
        "delta": s_cand - s_v025
    }

def main():
    print("=== Phase 2: Grandmaster Opening Controlled Experiment ===", flush=True)
    SEEDS = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]
    print(f"Testing {len(VARIANT_CONFIGS)} variants across {len(SEEDS)} paired seeds (20 matches per variant)...", flush=True)
    
    tasks = []
    for var_name in VARIANT_CONFIGS.keys():
        for s in SEEDS:
            tasks.append((var_name, s, True))
            tasks.append((var_name, s, False))
            
    print(f"Total matches to run: {len(tasks)} using 12 worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_match, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    summary = []
    for var_name, group in df.groupby("variant"):
        summary.append({
            "Variant": var_name,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Cand Mean ($)": group["cand_score"].mean(),
            "V025 Mean ($)": group["v025_score"].mean(),
            "Paired Delta ($)": group["delta"].mean(),
            "Delta Std ($)": group["delta"].std(),
            "Min Delta ($)": group["delta"].min(),
            "Max Delta ($)": group["delta"].max(),
        })
        
    summary_df = pd.DataFrame(summary).sort_values(by="Paired Delta ($)", ascending=False)
    print("\n=== SUMMARY RESULTS vs V025-A ===")
    print(summary_df.to_string(index=False))
    
    # Save results
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/phase2_opening_experiments.csv", index=False)
    summary_df.to_csv("experiments/phase2_opening_summary.csv", index=False)
    print("\nSaved detailed results to experiments/phase2_opening_summary.csv", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
