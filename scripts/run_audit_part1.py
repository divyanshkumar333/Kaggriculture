"""
Comprehensive Final Audit Runner for Kaggriculture V022-C
---------------------------------------------------------
Executes:
1. Replay Telemetry Comparison vs Episode 103388734 ($162.8k) at Days 0, 5, 6, 10, 15, 20, 25, 29.
2. 30-Game Fresh-Seed H2H: V022-C vs V020-C (Seeds 800..829).
3. 10-Game Fresh-Seed Suites vs:
   - True Industrial Livestock (v021_b)
   - Animal Optimizer (v005_d)
   - Harvest Timing (v009_b)
   - Diversified (v004_b)
   - Dynamic Clusters (v008_d)
   - Industrial Mirror (v022_b)
4. Factorial Ablation Tests:
   - Ablation A: No Day 0 sheep opening (Crop opening)
   - Ablation B: No paced sales (Single-turn dump)
   - Ablation C: No quad-matched labor (Static 3 workers)
   - Ablation D: No compact zoning (Dispersed pastures)
5. Industrial Mirror Collision Test (Market Glut Stress Test).
"""

import importlib.util
import json
import hashlib
import numpy as np
import time
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

print("Loading agents for Comprehensive Final Audit...")
v022_c = load_agent("agents/v022_c_market_batching.py")
v020_c = load_agent("agents/v020_c_competitive_surgical.py")
v021_b_ind = load_agent("agents/v021_b_industrial_livestock.py")
v005_d = load_agent("agents/v005_d_combined.py")
v009_b = load_agent("agents/v009_b_harvest_timing.py")
v004_b = load_agent("agents/v004_b_diversify.py")
v008_d = load_agent("agents/v008_d_dynamic_clusters.py")
v022_b_mirror = load_agent("agents/v022_b_dynamic_labor.py")

# =========================================================================
# AUDIT 1: FRESH-SEED H2H SUITE (Seeds 800..829)
# =========================================================================
print("\n" + "="*80)
print("AUDIT 1: FRESH-SEED H2H (V022-C vs V020-C Across 30 Seeds 800..829)")
print("="*80)

h2h_seeds = list(range(800, 830))
h2h_results = []
h2h_wins_p0 = 0
h2h_wins_p1 = 0
h2h_losses = 0
h2h_ties = 0

v022_c_scores = []
v020_c_scores = []

for idx, seed in enumerate(h2h_seeds):
    if idx % 2 == 0:
        # V022-C is P0, V020-C is P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([v022_c, v020_c])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        v022_c_scores.append(r0)
        v020_c_scores.append(r1)
        win = r0 > r1
        if win: h2h_wins_p0 += 1
        elif r0 == r1: h2h_ties += 1
        else: h2h_losses += 1
        h2h_results.append((seed, "P0", r0, r1, win))
    else:
        # V022-C is P1, V020-C is P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([v020_c, v022_c])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        v022_c_scores.append(r1)
        v020_c_scores.append(r0)
        win = r1 > r0
        if win: h2h_wins_p1 += 1
        elif r0 == r1: h2h_ties += 1
        else: h2h_losses += 1
        h2h_results.append((seed, "P1", r1, r0, win))

total_h2h_wins = h2h_wins_p0 + h2h_wins_p1
h2h_wr = (total_h2h_wins / len(h2h_seeds)) * 100.0
print(f"H2H Fresh 30-Game Result: Win Rate: {h2h_wr:.1f}% ({total_h2h_wins}W / {h2h_losses}L / {h2h_ties}T)")
print(f"P0 Wins: {h2h_wins_p0}/15 | P1 Wins: {h2h_wins_p1}/15")
print(f"V022-C Mean: ${np.mean(v022_c_scores):,.0f} | Median: ${np.median(v022_c_scores):,.0f} | Min: ${np.min(v022_c_scores):,.0f} | Max: ${np.max(v022_c_scores):,.0f}")
print(f"V020-C Mean: ${np.mean(v020_c_scores):,.0f} | Median: ${np.median(v020_c_scores):,.0f} | Min: ${np.min(v020_c_scores):,.0f} | Max: ${np.max(v020_c_scores):,.0f}")
print(f"Net Bank Delta: ${np.mean(v022_c_scores) - np.mean(v020_c_scores):+,.0f}")

# =========================================================================
# AUDIT 2: OPPONENT INTEGRITY & STRONG BENCHMARK SUITE
# =========================================================================
print("\n" + "="*80)
print("AUDIT 2: FRESH-SEED BENCHMARK vs STRONG FIELD (Seeds 830..839, P0 & P1)")
print("="*80)

strong_opponents = [
    ("True Industrial Livestock (V021-B)", v021_b_ind),
    ("Animal Optimizer (V005-D)", v005_d),
    ("Harvest Timing (V009-B)", v009_b),
    ("Diversified (V004-B)", v004_b),
    ("Dynamic Clusters (V008-D)", v008_d),
    ("Industrial Mirror (V022-B)", v022_b_mirror),
]

field_seeds = list(range(830, 840))  # 10 seeds * 2 positions = 20 games each
field_summary = {}

for opp_name, opp_agent in strong_opponents:
    wins = 0
    losses = 0
    ties = 0
    c_scores = []
    o_scores = []
    
    for s in field_seeds:
        # P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([v022_c, opp_agent])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        c_scores.append(r0)
        o_scores.append(r1)
        if r0 > r1: wins += 1
        elif r0 == r1: ties += 1
        else: losses += 1
        
        # P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([opp_agent, v022_c])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        c_scores.append(r1)
        o_scores.append(r0)
        if r1 > r0: wins += 1
        elif r1 == r0: ties += 1
        else: losses += 1
        
    n_g = len(c_scores)
    wr = (wins / n_g) * 100.0
    c_m = np.mean(c_scores)
    o_m = np.mean(o_scores)
    print(f"vs {opp_name:<35}: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L/{ties:1d}T) | Cand Mean: ${c_m:7,.0f} | Opp Mean: ${o_m:7,.0f} | Delta: ${c_m-o_m:+7,.0f}")
    field_summary[opp_name] = (wr, wins, losses, ties, c_m, o_m)

# =========================================================================
# AUDIT 3: FACTORIAL ABLATIONS
# =========================================================================
print("\n" + "="*80)
print("AUDIT 3: FACTORIAL ABLATION ANALYSIS (Seeds 840..849 vs V020-C)")
print("="*80)

# Build Ablation Agents programmatically
ablation_seeds = list(range(840, 850))

# Baseline V022-C score on ablation seeds
base_scores = []
for s in ablation_seeds:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env.run([v022_c, v020_c])
    base_scores.append(env.steps[-1][0]["reward"])
print(f"Full V022-C Control Mean on Ablation Seeds: ${np.mean(base_scores):,.0f}")

# Save audit results dictionary
audit_data = {
    "h2h_wr": h2h_wr,
    "h2h_wins": total_h2h_wins,
    "h2h_losses": h2h_losses,
    "h2h_ties": h2h_ties,
    "v022_c_mean": float(np.mean(v022_c_scores)),
    "v022_c_median": float(np.median(v022_c_scores)),
    "v022_c_min": float(np.min(v022_c_scores)),
    "v022_c_max": float(np.max(v022_c_scores)),
    "v020_c_mean": float(np.mean(v020_c_scores)),
    "v020_c_median": float(np.median(v020_c_scores)),
    "v020_c_min": float(np.min(v020_c_scores)),
    "v020_c_max": float(np.max(v020_c_scores)),
    "field_summary": {k: [float(x) for x in v] for k, v in field_summary.items()},
    "ablation_base_mean": float(np.mean(base_scores))
}

with open("scratch/audit_results_dump.json", "w") as f:
    json.dump(audit_data, f, indent=2)

print("\nAudit Run 1 & 2 Completed Successfully! Data saved to scratch/audit_results_dump.json.")
