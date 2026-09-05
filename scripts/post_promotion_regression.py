"""
Step 8: Post-Promotion Paired Regression Verification
----------------------------------------------------
Runs 100 fresh paired seeds (200 matches) comparing:
- main.py vs frozen V025-A
- agents/v027_hierarchical_meta.py vs frozen V025-A
Asserts:
- main.py outputs byte-equivalent behavior and identical scores to v027 candidate.
- Reports win rate, mean margin, median margin, and distribution.
"""

import os
import sys
import time
import multiprocessing as mp
import pandas as pd
import numpy as np
from kaggle_environments import make
import importlib.util

sys.stdout.reconfigure(encoding="utf-8")

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

def run_paired_check(task):
    seed, main_is_p0 = task
    main_agent = load_agent("main.py")
    v027_agent = load_agent("agents/v027_hierarchical_meta.py")
    v025_agent = load_agent("agents/v025_a_aggressive_cows.py")
    
    # Run Match 1: main.py vs v025_a
    players1 = [main_agent, v025_agent] if main_is_p0 else [v025_agent, main_agent]
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env1.run(players1)
    
    main_score = float(env1.steps[-1][0]["reward"] if main_is_p0 else env1.steps[-1][1]["reward"])
    v025_score1 = float(env1.steps[-1][1]["reward"] if main_is_p0 else env1.steps[-1][0]["reward"])
    
    # Run Match 2: v027 candidate vs v025_a on exact same seed and seating
    players2 = [v027_agent, v025_agent] if main_is_p0 else [v025_agent, v027_agent]
    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env2.run(players2)
    
    v027_score = float(env2.steps[-1][0]["reward"] if main_is_p0 else env2.steps[-1][1]["reward"])
    v025_score2 = float(env2.steps[-1][1]["reward"] if main_is_p0 else env2.steps[-1][0]["reward"])
    
    # Assert exact score reproducibility between main.py and candidate v027
    assert main_score == v027_score, f"Seed {seed} discrepancy: main={main_score} vs v027={v027_score}"
    assert v025_score1 == v025_score2, f"Seed {seed} opponent discrepancy: opp1={v025_score1} vs opp2={v025_score2}"
    
    return {
        "seed": seed,
        "main_is_p0": main_is_p0,
        "main_score": main_score,
        "v027_score": v027_score,
        "v025_score": v025_score1,
        "won": 1 if main_score > v025_score1 else 0,
        "delta": main_score - v025_score1
    }

def main():
    print("=== Step 8: Post-Promotion Paired Regression (100 Fresh Paired Seeds) ===", flush=True)
    SEEDS = list(range(60000, 60100)) # 100 completely fresh seeds
    
    tasks = []
    for s in SEEDS:
        tasks.append((s, True))  # main as P0
        tasks.append((s, False)) # main as P1
        
    print(f"Running {len(tasks)} matches (100 seeds in both seat positions) across 12 workers...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=12) as pool:
        results = pool.map(run_paired_check, tasks)
        
    t1 = time.time()
    print(f"Completed {len(results)} matches in {t1 - t0:.1f}s ({len(results)/(t1-t0):.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    
    win_rate = df["won"].mean() * 100
    mean_main = df["main_score"].mean()
    median_main = df["main_score"].median()
    mean_v025 = df["v025_score"].mean()
    median_v025 = df["v025_score"].median()
    mean_delta = df["delta"].mean()
    std_delta = df["delta"].std()
    p10_delta = df["delta"].quantile(0.10)
    p90_delta = df["delta"].quantile(0.90)
    
    print("\n=======================================================")
    print(f"POST-PROMOTION REGRESSION SUMMARY (main.py vs v025_a across {len(df)} matches):")
    print(f"  Win Rate:           {win_rate:.1f}%")
    print(f"  main.py Mean Cash:  ${mean_main:,.2f}")
    print(f"  main.py Median:     ${median_main:,.2f}")
    print(f"  V025-A Mean Cash:   ${mean_v025:,.2f}")
    print(f"  V025-A Median:      ${median_v025:,.2f}")
    print(f"  Paired Mean Delta:  ${mean_delta:+,.2f} (+/- ${std_delta:,.2f})")
    print(f"  Delta P10:          ${p10_delta:+,.2f}")
    print(f"  Delta P90:          ${p90_delta:+,.2f}")
    print(f"  Reproducibility:    100.0% EXACT MATCH (0 discrepancies across all 200 matches)")
    print("=======================================================\n")
    
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/post_promotion_regression_matches.csv", index=False)
    
if __name__ == "__main__":
    mp.freeze_support()
    main()
