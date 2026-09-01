"""
Comprehensive 108-Game Benchmark Harness for Agent V022-C
---------------------------------------------------------
Evaluates V022-C against 9 opponents across 12 unseen seeds (600..611),
playing both as Player 0 and Player 1 (24 games per opponent = 216 matchups).

Opponents:
1. V020-C (Frozen official champion)
2. Industrial Livestock (Pure livestock macro)
3. Animal Optimizer (V005-D)
4. Harvest Timing (V009-B)
5. Diversified (V004-B)
6. Dynamic Clusters (V008-D)
7. Melon Flooder
8. Starter Baseline
9. Random Baseline
"""

import importlib.util
import numpy as np
import time
from kaggle_environments import make

SEEDS = list(range(600, 612))  # 12 fresh unseen seeds

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_module", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

print("Loading agents for V022-C benchmark...")
v022_c = load_agent("agents/v022_c_market_batching.py")
v020_c = load_agent("agents/v020_c_competitive_surgical.py")
v005_d = load_agent("agents/v005_d_combined.py")
v009_b = load_agent("agents/v009_b_harvest_timing.py")
v004_b = load_agent("agents/v004_b_diversify.py")
v008_d = load_agent("agents/v008_d_dynamic_clusters.py")
opp_industrial = load_agent("agents/opp_industrial_livestock.py")
opp_melon = load_agent("agents/opp_melon_flooder.py")

OPPONENTS = [
    ("V020-C (Official Champion)", v020_c),
    ("Industrial Livestock", opp_industrial),
    ("Animal Optimizer (V005-D)", v005_d),
    ("Harvest Timing (V009-B)", v009_b),
    ("Diversified (V004-B)", v004_b),
    ("Dynamic Clusters (V008-D)", v008_d),
    ("Melon Flooder", opp_melon),
    ("Starter", "starter"),
    ("Random", "random"),
]

print("=" * 80)
print("STARTING V022-C BENCHMARK (108 MATCHUPS / 12 SEEDS / BOTH POSITIONS)")
print("=" * 80)

total_games = 0
total_wins = 0
total_ties = 0
total_cand_scores = []
total_opp_scores = []

overall_summary = []

for opp_name, opp_agent in OPPONENTS:
    t0 = time.time()
    wins = 0
    ties = 0
    losses = 0
    cand_scores = []
    opp_scores = []
    
    for seed in SEEDS:
        # Match 1: Candidate as Player 0
        try:
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
            env.run([v022_c, opp_agent])
            r0 = env.steps[-1][0]["reward"]
            r1 = env.steps[-1][1]["reward"]
            cand_scores.append(r0)
            opp_scores.append(r1)
            if r0 > r1: wins += 1
            elif r0 == r1: ties += 1
            else: losses += 1
        except Exception as e:
            print(f"Error on Seed {seed} P0 vs {opp_name}: {e}")
            losses += 1
            cand_scores.append(0)
            opp_scores.append(0)

        # Match 2: Candidate as Player 1
        try:
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
            env.run([opp_agent, v022_c])
            r0 = env.steps[-1][0]["reward"]
            r1 = env.steps[-1][1]["reward"]
            cand_scores.append(r1)
            opp_scores.append(r0)
            if r1 > r0: wins += 1
            elif r1 == r0: ties += 1
            else: losses += 1
        except Exception as e:
            print(f"Error on Seed {seed} P1 vs {opp_name}: {e}")
            losses += 1
            cand_scores.append(0)
            opp_scores.append(0)

    elapsed = time.time() - t0
    n_games = len(cand_scores)
    wr = (wins / n_games) * 100.0
    c_mean = np.mean(cand_scores)
    o_mean = np.mean(opp_scores)
    delta = c_mean - o_mean
    
    total_games += n_games
    total_wins += wins
    total_ties += ties
    total_cand_scores.extend(cand_scores)
    total_opp_scores.extend(opp_scores)
    
    print(f"vs {opp_name:<30}: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L/{ties:1d}T) | Cand Mean: ${c_mean:7,.0f} | Opp Mean: ${o_mean:7,.0f} | Delta: ${delta:+7,.0f} ({elapsed:4.1f}s)")
    overall_summary.append((opp_name, wr, wins, losses, ties, c_mean, o_mean, delta))

print("=" * 80)
overall_wr = (total_wins / total_games) * 100.0
overall_c_mean = np.mean(total_cand_scores)
overall_o_mean = np.mean(total_opp_scores)
print(f"OVERALL V022-C SCORECARD: {total_games} Games | Win Rate: {overall_wr:.1f}% ({total_wins}W/{total_games-total_wins-total_ties}L/{total_ties}T) | Mean Bank: ${overall_c_mean:,.0f} | Opp Mean: ${overall_o_mean:,.0f}")
print(f"Cand Min Score: ${np.min(total_cand_scores):,.0f} | Cand Max Score: ${np.max(total_cand_scores):,.0f}")
print("=" * 80)
