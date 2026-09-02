"""
V023 Official Multi-Adversary Benchmark Suite
---------------------------------------------
Evaluates Candidate V023-E against V022-C Champion Control, V020-C, V021-B,
and historical baselines on fresh seeds (920..939).
"""

import importlib.util
import numpy as np
import json
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v023_e = load_agent("agents/v023_e_cows_first_flywheel.py")
v022_c = load_agent("agents/v022_c_market_batching.py")
v020_c = load_agent("agents/v020_c_competitive_surgical.py")
v021_b = load_agent("agents/v021_b_industrial_livestock.py")

SEEDS = list(range(920, 935)) # 15 seeds * 2 positions = 30 games per matchup

print("="*95)
print("BENCHMARK TOURNAMENT: CANDIDATE V023-E vs BENCHMARK SUITE (30 GAMES PER MATCHUP)")
print("="*95)

MATCHUPS = [
    ("Candidate V023-E vs V022-C Champion", v023_e, v022_c),
    ("Candidate V023-E vs V020-C Surgical", v023_e, v020_c),
    ("Candidate V023-E vs V021-B Industrial", v023_e, v021_b),
]

tournament_results = {}

for label, cand_ag, opp_ag in MATCHUPS:
    c_scores, o_scores = [], []
    wins, losses, ties = 0, 0, 0
    for s in SEEDS:
        # P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([cand_ag, opp_ag])
        r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
        c_scores.append(r0); o_scores.append(r1)
        if r0 > r1: wins += 1
        elif r0 == r1: ties += 1
        else: losses += 1
        
        # P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([opp_ag, cand_ag])
        r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
        c_scores.append(r1); o_scores.append(r0)
        if r1 > r0: wins += 1
        elif r1 == r0: ties += 1
        else: losses += 1
        
    wr = (wins / len(c_scores)) * 100.0
    c_m = np.mean(c_scores)
    o_m = np.mean(o_scores)
    p25 = np.percentile(c_scores, 25)
    c_min = np.min(c_scores)
    c_max = np.max(c_scores)
    print(f"{label:<40}: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | Cand Mean: ${c_m:7,.0f} | Opp Mean: ${o_m:7,.0f} | Min: ${c_min:7,.0f} | Max: ${c_max:7,.0f} | Margin: ${c_m-o_m:+7,.0f}")
    tournament_results[label] = {
        "win_rate": wr, "wins": wins, "losses": losses, "cand_mean": float(c_m),
        "opp_mean": float(o_m), "p25": float(p25), "min": float(c_min), "max": float(c_max), "margin": float(c_m - o_m),
        "cand_scores": [float(x) for x in c_scores], "opp_scores": [float(x) for x in o_scores]
    }

with open("scratch/v023_benchmark_results.json", "w") as f:
    json.dump(tournament_results, f, indent=2)

print("\nSaved benchmark results to scratch/v023_benchmark_results.json")
