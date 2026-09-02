"""
V023 Counterfactual Experiment Suite
------------------------------------
Evaluates V023-A, V023-B, V023-C, V023-D against V022-C and V020-C across fresh seeds (900..909).
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

v020_c = load_agent("agents/v020_c_competitive_surgical.py")
v022_c = load_agent("agents/v022_c_market_batching.py")
v023_a = load_agent("agents/v023_a_cow_acceleration.py")
v023_b = load_agent("agents/v023_b_strawberry_early_ramp.py")
v023_c = load_agent("agents/v023_c_late_crop_succession.py")
v023_d = load_agent("agents/v023_d_integrated_flywheel.py")

CANDIDATES = [
    ("V022-C Control", v022_c),
    ("V023-A (Fast Cows)", v023_a),
    ("V023-B (Early Strawberries)", v023_b),
    ("V023-C (Late Succession)", v023_c),
    ("V023-D (Integrated Flywheel)", v023_d),
]

SEEDS = list(range(900, 910)) # 10 fresh seeds * 2 positions = 20 games each

print("="*95)
print("PART 1: CANDIDATES VS V020-C (20 GAMES EACH)")
print("="*95)

results_vs_v020 = {}

for name, ag in CANDIDATES:
    c_scores, o_scores = [], []
    wins, losses, ties = 0, 0, 0
    for s in SEEDS:
        # P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([ag, v020_c])
        r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
        c_scores.append(r0); o_scores.append(r1)
        if r0 > r1: wins += 1
        elif r0 == r1: ties += 1
        else: losses += 1
        
        # P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([v020_c, ag])
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
    print(f"{name:<30}: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | Mean: ${c_m:7,.0f} | 25th: ${p25:7,.0f} | Min: ${c_min:7,.0f} | Max: ${c_max:7,.0f} | Delta: ${c_m-o_m:+7,.0f}")
    results_vs_v020[name] = {
        "win_rate": wr, "wins": wins, "losses": losses, "mean": float(c_m),
        "p25": float(p25), "min": float(c_min), "max": float(c_max), "delta": float(c_m - o_m)
    }

print("\n" + "="*95)
print("PART 2: CANDIDATES DIRECT HEAD-TO-HEAD VS V022-C (20 GAMES EACH)")
print("="*95)

results_vs_v022 = {}

for name, ag in CANDIDATES[1:]: # Skip V022-C vs itself
    c_scores, o_scores = [], []
    wins, losses, ties = 0, 0, 0
    for s in SEEDS:
        # P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([ag, v022_c])
        r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
        c_scores.append(r0); o_scores.append(r1)
        if r0 > r1: wins += 1
        elif r0 == r1: ties += 1
        else: losses += 1
        
        # P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([v022_c, ag])
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
    print(f"{name:<30} vs V022-C: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | Cand Mean: ${c_m:7,.0f} | V22 Mean: ${o_m:7,.0f} | Delta: ${c_m-o_m:+7,.0f}")
    results_vs_v022[name] = {
        "win_rate": wr, "wins": wins, "losses": losses, "mean": float(c_m),
        "v22_mean": float(o_m), "delta": float(c_m - o_m)
    }

with open("scratch/v023_counterfactual_results.json", "w") as f:
    json.dump({"vs_v020": results_vs_v020, "vs_v022": results_vs_v022}, f, indent=2)

print("\nSaved counterfactual results to scratch/v023_counterfactual_results.json")
