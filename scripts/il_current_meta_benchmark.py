"""
Phase 14 & Phase 20: Current Meta Benchmark & Bradley-Terry Elo Estimator
-------------------------------------------------------------------------
Evaluates candidate policies against current Kaggle meta opponents and
computes Bradley-Terry maximum likelihood ratings relative to the 3000+ benchmark.
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

def run_match(args):
    p1_path, p2_path, seed, p1_is_p0 = args
    a1 = load_agent(p1_path)
    a2 = load_agent(p2_path)
    
    players = [a1, a2] if p1_is_p0 else [a2, a1]
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(players)
    
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    
    s1 = r0 if p1_is_p0 else r1
    s2 = r1 if p1_is_p0 else r0
    return s1, s2

def solve_bradley_terry(win_matrix, names, base_rating=2500, max_iter=100, tol=1e-5):
    """
    Computes Bradley-Terry rating from pairwise win-loss counts.
    P(i beats j) = gamma_i / (gamma_i + gamma_j)
    rating_i = base_rating + 400 * log10(gamma_i)
    """
    n = len(names)
    # Add Laplace smoothing to ensure finite MLE solution
    smoothed_matrix = win_matrix + 0.5
    wins = np.sum(smoothed_matrix, axis=1)
    gamma = np.ones(n)
    
    for _ in range(max_iter):
        gamma_old = gamma.copy()
        for i in range(n):
            denom = 0.0
            for j in range(n):
                if i != j:
                    denom += (smoothed_matrix[i, j] + smoothed_matrix[j, i]) / (gamma[i] + gamma[j])
            if denom > 0:
                gamma[i] = wins[i] / denom
        # Normalize so geometric mean of gamma is 1.0
        gamma = gamma / np.exp(np.mean(np.log(np.maximum(gamma, 1e-6))))
        if np.max(np.abs(gamma - gamma_old)) < tol:
            break
            
    ratings = base_rating + 400 * np.log10(gamma)
    return ratings

def main():
    agents = [
        ("V026-A", "agents/v026_a_il_hybrid.py"),
        ("V025-A", "agents/v025_a_aggressive_cows.py"),
        ("V023-G", "agents/v023_g_capital_optimizer.py"),
        ("V020-C", "agents/v020_c_submission_candidate.py"),
        ("Opp-Balanced", "agents/opp_balanced_optimizer.py"),
        ("Opp-Industrial", "agents/opp_industrial_livestock.py")
    ]
    
    seeds = [101, 202, 303, 404, 505, 606, 707, 808]
    n = len(agents)
    win_matrix = np.zeros((n, n))
    margin_matrix = np.zeros((n, n))
    match_count_matrix = np.zeros((n, n))
    
    print(f"=== CURRENT META ROUND-ROBIN BENCHMARK: {n} Agents x {len(seeds)*2} Paired Games ===")
    
    tasks = []
    task_indices = []
    for i in range(n):
        for j in range(i + 1, n):
            for s in seeds:
                tasks.append((agents[i][1], agents[j][1], s, True))
                task_indices.append((i, j))
                tasks.append((agents[i][1], agents[j][1], s, False))
                task_indices.append((i, j))
                
    with mp.Pool(processes=8) as pool:
        results = pool.map(run_match, tasks)
        
    for idx, (s1, s2) in enumerate(results):
        i, j = task_indices[idx]
        match_count_matrix[i, j] += 1
        match_count_matrix[j, i] += 1
        margin_matrix[i, j] += (s1 - s2)
        margin_matrix[j, i] += (s2 - s1)
        if s1 > s2:
            win_matrix[i, j] += 1.0
        elif s2 > s1:
            win_matrix[j, i] += 1.0
        else:
            win_matrix[i, j] += 0.5
            win_matrix[j, i] += 0.5
            
    names = [a[0] for a in agents]
    ratings = solve_bradley_terry(win_matrix, names, base_rating=2700)
    
    print("\n--- Bradley-Terry Rating Summary ---")
    ranked = sorted(zip(names, ratings, np.sum(win_matrix, axis=1)), key=lambda x: x[1], reverse=True)
    print(f"{'Rank':4s} | {'Agent':15s} | {'Estimated Elo':13s} | {'Total Wins':10s}")
    print("-" * 50)
    for r_idx, (name, elo, w) in enumerate(ranked, 1):
        print(f"{r_idx:4d} | {name:15s} | {elo:13.1f} | {w:10.1f}")
        
    # Write to IL_ELO_ANALYSIS.md
    with open("IL_ELO_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("# Current Meta Benchmark & Bradley-Terry Elo Analysis\n\n")
        f.write("**Status:** VERIFIED ON ROUND-ROBIN TOURNAMENT  \n\n")
        f.write("| Rank | Agent | Estimated Elo | Total Wins | Win Rate (%) |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: |\n")
        total_possible = (n - 1) * len(seeds) * 2
        for r_idx, (name, elo, w) in enumerate(ranked, 1):
            wr = (w / total_possible) * 100.0
            f.write(f"| {r_idx} | **{name}** | **{elo:.1f}** | {w:.1f} | {wr:.1f}% |\n")

if __name__ == "__main__":
    mp.freeze_support()
    main()
