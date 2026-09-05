"""
Phase 9: Massive Fresh-Seed Validation Tournament
-------------------------------------------------
Evaluates candidate V027 against:
- 500 fresh paired seeds vs V025-A (1,000 matches)
- 500 fresh paired seeds vs V023-G (1,000 matches)
- 300 fresh paired seeds vs V022-C (600 matches)
- 300 fresh paired seeds vs V020-C (600 matches)
- 100 fresh paired seeds vs Random (200 matches)
Total: 3,400 matches across mirrored player positions (Seat 0 and Seat 1).
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

def run_tournament_match(task):
    cand_path, opp_path, seed, cand_is_p0 = task
    cand_agent = load_agent(cand_path)
    
    if opp_path == "random":
        opp_agent = "random"
    else:
        opp_agent = load_agent(opp_path)
        
    if cand_is_p0:
        players = [cand_agent, opp_agent]
    else:
        players = [opp_agent, cand_agent]
        
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(players)
    
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    
    cand_score = r0 if cand_is_p0 else r1
    opp_score = r1 if cand_is_p0 else r0
    
    cand_idx = 0 if cand_is_p0 else 1
    
    # Check for structural failure (reward == 0 or negative or error status)
    status0 = env.steps[-1][0]["status"]
    status1 = env.steps[-1][1]["status"]
    cand_status = status0 if cand_is_p0 else status1
    is_structural_failure = 1 if (cand_status != "DONE" or cand_score <= 0) else 0
    
    return {
        "opponent": os.path.basename(opp_path).replace(".py", "") if opp_path != "random" else "Random",
        "seed": seed,
        "cand_is_p0": cand_is_p0,
        "cand_score": cand_score,
        "opp_score": opp_score,
        "won": 1 if cand_score > opp_score else 0,
        "tied": 1 if cand_score == opp_score else 0,
        "lost": 1 if cand_score < opp_score else 0,
        "delta": cand_score - opp_score,
        "structural_failure": is_structural_failure
    }

def run_benchmark_suite(cand_file, num_workers=12):
    print(f"=== Running Massive Validation Tournament for {cand_file} ===", flush=True)
    
    opponents_config = [
        ("agents/v025_a_aggressive_cows.py", 500, 10000),   # 500 seeds starting at 10000
        ("agents/v023_g_capital_optimizer.py", 500, 20000),  # 500 seeds starting at 20000
        ("agents/v022_c_market_batching.py", 300, 30000),   # 300 seeds starting at 30000
        ("agents/v020_c_competitive_surgical.py", 300, 40000), # 300 seeds starting at 40000
        ("random", 100, 50000),                            # 100 seeds starting at 50000
    ]
    
    all_tasks = []
    for opp_path, num_seeds, seed_start in opponents_config:
        seeds = list(range(seed_start, seed_start + num_seeds))
        for s in seeds:
            all_tasks.append((cand_file, opp_path, s, True))
            all_tasks.append((cand_file, opp_path, s, False))
            
    total_matches = len(all_tasks)
    print(f"Total Matches to execute: {total_matches} across {num_workers} worker processes...", flush=True)
    t0 = time.time()
    
    with mp.Pool(processes=num_workers) as pool:
        results = pool.map(run_tournament_match, all_tasks)
        
    t1 = time.time()
    elapsed = t1 - t0
    print(f"\nTournament completed in {elapsed:.1f}s ({total_matches/elapsed:.1f} matches/s)", flush=True)
    
    df = pd.DataFrame(results)
    os.makedirs("experiments", exist_ok=True)
    df.to_csv("experiments/v027_massive_tournament_matches.csv", index=False)
    
    summary_rows = []
    for opp_name, group in df.groupby("opponent"):
        summary_rows.append({
            "Opponent": opp_name,
            "Matches": len(group),
            "Win Rate (%)": group["won"].mean() * 100,
            "Loss Rate (%)": group["lost"].mean() * 100,
            "Tie Rate (%)": group["tied"].mean() * 100,
            "Cand Mean ($)": group["cand_score"].mean(),
            "Cand Median ($)": group["cand_score"].median(),
            "Opp Mean ($)": group["opp_score"].mean(),
            "Opp Median ($)": group["opp_score"].median(),
            "Paired Mean Delta ($)": group["delta"].mean(),
            "Delta P10 ($)": group["delta"].quantile(0.10),
            "Delta P90 ($)": group["delta"].quantile(0.90),
            "Worst Delta ($)": group["delta"].min(),
            "Best Delta ($)": group["delta"].max(),
            "Delta Std ($)": group["delta"].std(),
            "Structural Failures": group["structural_failure"].sum(),
        })
        
    sum_df = pd.DataFrame(summary_rows).sort_values(by="Matches", ascending=False)
    print("\n=== MASSIVE VALIDATION TOURNAMENT SUMMARY ===")
    print(sum_df.to_string(index=False))
    sum_df.to_csv("experiments/v027_massive_tournament_summary.csv", index=False)
    
    return sum_df

if __name__ == "__main__":
    mp.freeze_support()
    cand = "agents/v027_hierarchical_meta.py"
    if len(sys.argv) > 1:
        cand = sys.argv[1]
    run_benchmark_suite(cand, num_workers=12)
