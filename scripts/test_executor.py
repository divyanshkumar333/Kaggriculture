import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import time
import concurrent.futures
from scipy.optimize import linear_sum_assignment
from kaggle_environments import make
import importlib.util

spec_a = importlib.util.spec_from_file_location("mod_a", "agents/v025_a_aggressive_cows.py")
mod_a = importlib.util.module_from_spec(spec_a)
spec_a.loader.exec_module(mod_a)
agent_a = mod_a.agent

spec_g = importlib.util.spec_from_file_location("mod_g", "agents/v023_g_capital_optimizer.py")
mod_g = importlib.util.module_from_spec(spec_g)
spec_g.loader.exec_module(mod_g)
agent_g = mod_g.agent

def run_game(seed):
    t0 = time.time()
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([agent_a, agent_g])
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    dt = time.time() - t0
    return seed, r0, r1, dt

def main():
    t_start = time.time()
    seeds = [101, 102, 103, 104]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        for res in executor.map(run_game, seeds):
            print(f"Seed {res[0]}: {res[1]:,.0f} vs {res[2]:,.0f} ({res[3]:.1f}s)", flush=True)
    print(f"Total time for 4 games: {time.time() - t_start:.1f}s", flush=True)

if __name__ == "__main__":
    main()
