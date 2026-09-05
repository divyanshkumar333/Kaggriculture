"""
Deterministic Regression Tests for Promoted main.py
"""

import importlib.util
import time
import numpy as np
from kaggle_environments import make

spec_main = importlib.util.spec_from_file_location('main', 'main.py')
mod_main = importlib.util.module_from_spec(spec_main)
spec_main.loader.exec_module(mod_main)

spec_g = importlib.util.spec_from_file_location('g', 'agents/v023_g_capital_optimizer.py')
mod_g = importlib.util.module_from_spec(spec_g)
spec_g.loader.exec_module(mod_g)

print("=== 1. DETERMINISTIC REGRESSION SET (main.py vs Random) ===")
rand_seeds = [42, 100, 200, 500, 1000]
rand_results = {}
for s in rand_seeds:
    t0 = time.time()
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': s}, debug=False)
    env.run([mod_main.agent, 'random'])
    r0 = float(env.steps[-1][0]['reward'])
    r1 = float(env.steps[-1][1]['reward'])
    dt = time.time() - t0
    rand_results[s] = (r0, r1, dt)
    print(f"Seed {s:4d}: main.py = ${r0:,.0f} | Random = ${r1:,.0f} ({dt:.2f}s)")

print("\n=== 2. H2H REGRESSION SET: main.py vs V023-G (20 paired seeds = 40 games) ===")
paired_seeds = list(range(9000, 9020))
main_scores = []
g_scores = []
wins = 0
losses = 0
ties = 0

for idx, s in enumerate(paired_seeds, 1):
    # Game 1: main.py as P0, V023-G as P1
    env1 = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': s}, debug=False)
    env1.run([mod_main.agent, mod_g.agent])
    r0_1 = float(env1.steps[-1][0]['reward'])
    r1_1 = float(env1.steps[-1][1]['reward'])
    main_scores.append(r0_1)
    g_scores.append(r1_1)
    if r0_1 > r1_1: wins += 1
    elif r0_1 < r1_1: losses += 1
    else: ties += 1

    # Game 2: V023-G as P0, main.py as P1
    env2 = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': s}, debug=False)
    env2.run([mod_g.agent, mod_main.agent])
    r0_2 = float(env2.steps[-1][0]['reward'])
    r1_2 = float(env2.steps[-1][1]['reward'])
    g_scores.append(r0_2)
    main_scores.append(r1_2)
    if r1_2 > r0_2: wins += 1
    elif r1_2 < r0_2: losses += 1
    else: ties += 1
    
    print(f"Pair {idx:2d} (Seed {s:4d}): P0_main=${r0_1:,.0f} vs P1_g=${r1_1:,.0f} | P0_g=${r0_2:,.0f} vs P1_main=${r1_2:,.0f}")

main_mean = float(np.mean(main_scores))
g_mean = float(np.mean(g_scores))
delta = main_mean - g_mean
win_rate = (wins / len(main_scores)) * 100.0

print(f"\n--- SUMMARY ---")
print(f"Total Games: {len(main_scores)}")
print(f"Wins: {wins}, Losses: {losses}, Ties: {ties}")
print(f"Win Rate: {win_rate:.2f}%")
print(f"main.py Mean: ${main_mean:,.2f}")
print(f"V023-G  Mean: ${g_mean:,.2f}")
print(f"Paired Delta: +${delta:,.2f}")
