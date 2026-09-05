"""
Phase 11 & Phase 19: Comprehensive Policy Evaluation Tournament
---------------------------------------------------------------
Evaluates imitation-learning candidates against the promoted gold standard (V025-A)
and key competitive controls (V023-G, V022-C, V020-C, V021-B Industrial).

Uses multiprocessing across CPU cores with paired mirror matches (both P0 and P1).
Calculates:
- Mean & Median Final Bank
- P10, P25, P75, P90
- Win Rate (%)
- Paired Delta ($)
- Standard Deviation
"""

import os
import sys
import time
import multiprocessing as mp
import importlib.util
import numpy as np
from kaggle_environments import make

sys.stdout.reconfigure(encoding="utf-8")

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

def run_single_match(args):
    agent1_path, agent2_path, seed, p1_is_p0 = args
    a1 = load_agent(agent1_path)
    a2 = load_agent(agent2_path)
    
    if p1_is_p0:
        players = [a1, a2]
    else:
        players = [a2, a1]
        
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(players)
    
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    
    if p1_is_p0:
        score_candidate = r0
        score_opponent = r1
    else:
        score_candidate = r1
        score_opponent = r0
        
    return seed, p1_is_p0, score_candidate, score_opponent

def evaluate_pairing(cand_path, opp_path, seeds, num_workers=8):
    cand_name = os.path.basename(cand_path).replace(".py", "")
    opp_name = os.path.basename(opp_path).replace(".py", "")
    
    tasks = []
    for s in seeds:
        tasks.append((cand_path, opp_path, s, True))   # Candidate as P0
        tasks.append((cand_path, opp_path, s, False))  # Candidate as P1
        
    t0 = time.time()
    cand_scores = []
    opp_scores = []
    wins = 0
    losses = 0
    ties = 0
    
    with mp.Pool(processes=num_workers) as pool:
        for res in pool.imap_unordered(run_single_match, tasks):
            seed, is_p0, s_cand, s_opp = res
            cand_scores.append(s_cand)
            opp_scores.append(s_opp)
            if s_cand > s_opp:
                wins += 1
            elif s_opp > s_cand:
                losses += 1
            else:
                ties += 1
                
    elapsed = time.time() - t0
    total = len(tasks)
    win_rate = (wins / total) * 100.0
    cand_scores = np.array(cand_scores)
    opp_scores = np.array(opp_scores)
    deltas = cand_scores - opp_scores
    
    res = {
        "candidate": cand_name,
        "opponent": opp_name,
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": win_rate,
        "cand_mean": np.mean(cand_scores),
        "cand_median": np.median(cand_scores),
        "cand_p10": np.percentile(cand_scores, 10),
        "cand_p25": np.percentile(cand_scores, 25),
        "cand_p75": np.percentile(cand_scores, 75),
        "cand_p90": np.percentile(cand_scores, 90),
        "cand_std": np.std(cand_scores),
        "opp_mean": np.mean(opp_scores),
        "opp_median": np.median(opp_scores),
        "mean_delta": np.mean(deltas),
        "median_delta": np.median(deltas),
        "elapsed_sec": elapsed
    }
    return res

def main():
    seeds = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909, 1001, 1102, 1203, 1304, 1405]
    print(f"=== TOURNAMENT: {len(seeds)} Seeds x 2 Positions = {len(seeds)*2} Games per Matchup ===")
    
    candidates = [
        "agents/v026_a_il_hybrid.py",
        "agents/v026_b_il_gbdt.py",
        "agents/v026_c_il_pure_imitation.py",
        "agents/v026_d_il_conservative.py",
    ]
    
    primary_opponent = "agents/v025_a_aggressive_cows.py"
    
    all_results = []
    print(f"\n--- Round 1: All IL Candidates vs Promoted Gold Standard ({os.path.basename(primary_opponent)}) ---")
    header = f"{'Candidate':25s} | {'Win Rate':9s} | {'Cand Mean':11s} | {'Opp Mean':11s} | {'Net Margin':11s} | {'Cand Med':11s}"
    print(header)
    print("-" * len(header))
    
    for cand in candidates:
        r = evaluate_pairing(cand, primary_opponent, seeds, num_workers=8)
        all_results.append(r)
        print(f"{r['candidate']:25s} | {r['win_rate']:7.1f}% | ${r['cand_mean']:10,.0f} | ${r['opp_mean']:10,.0f} | ${r['mean_delta']:+10,.0f} | ${r['cand_median']:10,.0f}")
        
    print("\n--- Round 2: Leading Candidate vs Historical Tournament Controls ---")
    best_cand = "agents/v026_a_il_hybrid.py"
    controls = [
        "agents/v023_g_capital_optimizer.py",
        "agents/v022_c_market_batching.py",
        "agents/v020_c_submission_candidate.py",
        "agents/v021_b_industrial_livestock.py",
    ]
    for ctrl in controls:
        r = evaluate_pairing(best_cand, ctrl, seeds, num_workers=8)
        all_results.append(r)
        print(f"V026-A vs {r['opponent']:25s} | Win Rate: {r['win_rate']:5.1f}% | Cand Mean: ${r['cand_mean']:,.0f} | Opp Mean: ${r['opp_mean']:,.0f} | Net Margin: ${r['mean_delta']:+,.0f}")
        
    # Write summary markdown report
    with open("IL_EVALUATION_RESULTS.md", "w", encoding="utf-8") as f:
        f.write("# IL Policy Evaluation Tournament Results\n\n")
        f.write(f"**Date:** September 5, 2026  \n")
        f.write(f"**Configuration:** {len(seeds)} Paired Seeds ({len(seeds)*2} games per pairing) across 8 parallel worker processes.\n\n")
        f.write("## 1. Candidate vs V025-A Head-to-Head\n\n")
        f.write("| Candidate | Win Rate (%) | Candidate Mean ($) | V025-A Mean ($) | Net Margin ($) | Candidate Median ($) | P10 ($) | P90 ($) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in all_results:
            if r["opponent"] == "v025_a_aggressive_cows":
                f.write(f"| `{r['candidate']}` | **{r['win_rate']:.1f}%** | ${r['cand_mean']:,.0f} | ${r['opp_mean']:,.0f} | **${r['mean_delta']:+,.0f}** | ${r['cand_median']:,.0f} | ${r['cand_p10']:,.0f} | ${r['cand_p90']:,.0f} |\n")
        f.write("\n## 2. V026-A vs Historical Benchmark Suite\n\n")
        f.write("| Opponent | Win Rate (%) | V026-A Mean ($) | Opponent Mean ($) | Net Margin ($) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for r in all_results:
            if r["opponent"] != "v025_a_aggressive_cows":
                f.write(f"| `{r['opponent']}` | **{r['win_rate']:.1f}%** | ${r['cand_mean']:,.0f} | ${r['opp_mean']:,.0f} | **${r['mean_delta']:+,.0f}** |\n")

if __name__ == "__main__":
    mp.freeze_support()
    main()
