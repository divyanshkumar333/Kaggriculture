"""
Tournament: Candidate V025-F vs Leading Candidate V025-A
=========================================================
Runs 300 fresh paired seeds (600 games total).
Tests both player positions:
- P0: V025-F vs P1: V025-A
- P0: V025-A vs P1: V025-F

Computes primary metrics:
- Mean
- Median
- P10
- P25
- Minimum
- Maximum
- Standard deviation
- Paired delta
- Win rate
"""

import multiprocessing as mp
import numpy as np
import pandas as pd
import json
import os
import importlib.util
from kaggle_environments import make

def run_paired_game(seed):
    spec_f = importlib.util.spec_from_file_location("mod_f", "agents/v025_f_adaptive_flywheel.py")
    mod_f = importlib.util.module_from_spec(spec_f)
    spec_f.loader.exec_module(mod_f)
    agent_f = mod_f.agent

    spec_a = importlib.util.spec_from_file_location("mod_a", "agents/v025_a_aggressive_cows.py")
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    agent_a = mod_a.agent

    # Game 1: F as P0, A as P1
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env0.run([agent_f, agent_a])
    r_f0 = float(env0.steps[-1][0]["reward"])
    r_a0 = float(env0.steps[-1][1]["reward"])

    # Game 2: A as P0, F as P1
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env1.run([agent_a, agent_f])
    r_a1 = float(env1.steps[-1][0]["reward"])
    r_f1 = float(env1.steps[-1][1]["reward"])

    return {
        "seed": seed,
        "f_scores": [r_f0, r_f1],
        "a_scores": [r_a0, r_a1],
        "f_wins": int(r_f0 > r_a0) + int(r_f1 > r_a1),
        "a_wins": int(r_a0 > r_f0) + int(r_a1 > r_f1),
        "deltas": [r_f0 - r_a0, r_f1 - r_a1]
    }

def main():
    seeds = list(range(7000, 7300)) # 300 fresh seeds = 600 games
    pool_size = min(8, mp.cpu_count())
    print("="*100)
    print(f"RUNNING 300-SEED (600 GAMES) TOURNAMENT: V025-F VS V025-A ON {pool_size} CORES")
    print("="*100)

    results = []
    with mp.Pool(processes=pool_size) as pool:
        for i, res in enumerate(pool.imap_unordered(run_paired_game, seeds), 1):
            results.append(res)
            if i % 50 == 0 or i == len(seeds):
                f_all = [s for r in results for s in r["f_scores"]]
                a_all = [s for r in results for s in r["a_scores"]]
                f_w = sum(r["f_wins"] for r in results)
                tot = len(f_all)
                print(f"Progress: {i}/{len(seeds)} seeds ({tot} games) | V025-F WR: {(f_w/tot)*100:.1f}% | Mean F: ${np.mean(f_all):,.0f} | Mean A: ${np.mean(a_all):,.0f} | Delta: +${np.mean(f_all)-np.mean(a_all):,.0f}", flush=True)

    all_f_scores = [s for r in results for s in r["f_scores"]]
    all_a_scores = [s for r in results for s in r["a_scores"]]
    all_deltas = [d for r in results for d in r["deltas"]]
    total_games = len(all_f_scores)
    total_f_wins = sum(r["f_wins"] for r in results)
    total_a_wins = sum(r["a_wins"] for r in results)

    stats = {
        "total_seeds": len(seeds),
        "total_games": total_games,
        "v025_f": {
            "mean": float(np.mean(all_f_scores)),
            "median": float(np.median(all_f_scores)),
            "std": float(np.std(all_f_scores)),
            "p10": float(np.percentile(all_f_scores, 10)),
            "p25": float(np.percentile(all_f_scores, 25)),
            "p75": float(np.percentile(all_f_scores, 75)),
            "p90": float(np.percentile(all_f_scores, 90)),
            "min": float(np.min(all_f_scores)),
            "max": float(np.max(all_f_scores)),
            "wins": total_f_wins,
            "win_rate": float((total_f_wins / total_games) * 100.0)
        },
        "v025_a": {
            "mean": float(np.mean(all_a_scores)),
            "median": float(np.median(all_a_scores)),
            "std": float(np.std(all_a_scores)),
            "p10": float(np.percentile(all_a_scores, 10)),
            "p25": float(np.percentile(all_a_scores, 25)),
            "p75": float(np.percentile(all_a_scores, 75)),
            "p90": float(np.percentile(all_a_scores, 90)),
            "min": float(np.min(all_a_scores)),
            "max": float(np.max(all_a_scores)),
            "wins": total_a_wins,
            "win_rate": float((total_a_wins / total_games) * 100.0)
        },
        "paired_delta": {
            "mean": float(np.mean(all_deltas)),
            "median": float(np.median(all_deltas)),
            "std": float(np.std(all_deltas))
        }
    }

    os.makedirs("scratch", exist_ok=True)
    with open("scratch/v025_f_large_scale_results.json", "w") as f:
        json.dump(stats, f, indent=2)

    print("\n" + "="*100)
    print("FINAL 300-SEED TOURNAMENT SUMMARY: V025-F VS V025-A")
    print("="*100)
    print(f"V025-F Mean:   ${stats['v025_f']['mean']:,.0f} | Median: ${stats['v025_f']['median']:,.0f} | P10: ${stats['v025_f']['p10']:,.0f} | P25: ${stats['v025_f']['p25']:,.0f} | Min: ${stats['v025_f']['min']:,.0f} | Max: ${stats['v025_f']['max']:,.0f}")
    print(f"V025-A Mean:   ${stats['v025_a']['mean']:,.0f} | Median: ${stats['v025_a']['median']:,.0f} | P10: ${stats['v025_a']['p10']:,.0f} | P25: ${stats['v025_a']['p25']:,.0f} | Min: ${stats['v025_a']['min']:,.0f} | Max: ${stats['v025_a']['max']:,.0f}")
    print(f"Paired Delta:  +${stats['paired_delta']['mean']:,.0f} (Mean) | +${stats['paired_delta']['median']:,.0f} (Median)")
    print(f"V025-F Win Rate: {stats['v025_f']['win_rate']:.2f}% ({total_f_wins}/{total_games})")
    print("="*100)

if __name__ == "__main__":
    mp.freeze_support()
    main()
