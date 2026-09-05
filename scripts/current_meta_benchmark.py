"""
Current Meta Benchmark: Evaluate candidates against historical controls and top meta policies
"""

import sys
import time
import importlib.util
import numpy as np
from kaggle_environments import make

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def load_agent(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_h2h(agent1_path, agent2_path, num_pairs=25, start_seed=10000):
    a1 = load_agent(agent1_path)
    a2 = load_agent(agent2_path)
    
    a1_name = agent1_path.split("/")[-1].replace(".py", "")
    a2_name = agent2_path.split("/")[-1].replace(".py", "")
    
    scores1 = []
    scores2 = []
    wins1 = 0
    wins2 = 0
    ties = 0
    
    t0 = time.time()
    for i in range(num_pairs):
        seed = start_seed + i
        
        # Game 1: a1 as P0, a2 as P1
        env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env1.run([a1, a2])
        r0 = float(env1.steps[-1][0]["reward"])
        r1 = float(env1.steps[-1][1]["reward"])
        scores1.append(r0)
        scores2.append(r1)
        if r0 > r1: wins1 += 1
        elif r1 > r0: wins2 += 1
        else: ties += 1
        
        # Game 2: a2 as P0, a1 as P1
        env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env2.run([a2, a1])
        r0_2 = float(env2.steps[-1][0]["reward"])
        r1_2 = float(env2.steps[-1][1]["reward"])
        scores2.append(r0_2)
        scores1.append(r1_2)
        if r1_2 > r0_2: wins1 += 1
        elif r0_2 > r1_2: wins2 += 1
        else: ties += 1
        
    dt = time.time() - t0
    total_games = num_pairs * 2
    win_rate = (wins1 / total_games) * 100.0
    mean1 = float(np.mean(scores1))
    mean2 = float(np.mean(scores2))
    delta = mean1 - mean2
    
    print(f"\n{'='*70}")
    print(f"H2H TOURNAMENT: {a1_name} vs {a2_name} ({total_games} games in {dt:.1f}s)")
    print(f"{'='*70}")
    print(f"{a1_name:25s}: {wins1:2d}W ({win_rate:5.1f}%) | Mean: ${mean1:>9,.2f} | Med: ${np.median(scores1):>9,.2f}")
    print(f"{a2_name:25s}: {wins2:2d}W ({(wins2/total_games)*100:5.1f}%) | Mean: ${mean2:>9,.2f} | Med: ${np.median(scores2):>9,.2f}")
    print(f"Paired Delta: {delta:+,.2f}")
    return win_rate, delta, mean1, mean2

if __name__ == "__main__":
    cand = sys.argv[1] if len(sys.argv) > 1 else "agents/v025_a_aggressive_cows.py"
    opp = sys.argv[2] if len(sys.argv) > 2 else "agents/v023_g_capital_optimizer.py"
    n_pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 25
    run_h2h(cand, opp, num_pairs=n_pairs)
