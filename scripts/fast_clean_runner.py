import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import time
import concurrent.futures
from kaggle_environments import make
import importlib.util

def run_single_game(args):
    seed, agent_name_a, agent_name_b = args
    
    # Load A
    if agent_name_a == "v25f":
        spec_a = importlib.util.spec_from_file_location("mod_a", "agents/v025_f_adaptive_flywheel.py")
    elif agent_name_a == "v25a":
        spec_a = importlib.util.spec_from_file_location("mod_a", "agents/v025_a_aggressive_cows.py")
    else:
        spec_a = importlib.util.spec_from_file_location("mod_a", "agents/v023_g_capital_optimizer.py")
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    agent_a = mod_a.agent

    # Load B
    if agent_name_b == "v25f":
        spec_b = importlib.util.spec_from_file_location("mod_b", "agents/v025_f_adaptive_flywheel.py")
    elif agent_name_b == "v25a":
        spec_b = importlib.util.spec_from_file_location("mod_b", "agents/v025_a_aggressive_cows.py")
    else:
        spec_b = importlib.util.spec_from_file_location("mod_b", "agents/v023_g_capital_optimizer.py")
    mod_b = importlib.util.module_from_spec(spec_b)
    spec_b.loader.exec_module(mod_b)
    agent_b = mod_b.agent

    t0 = time.time()
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([agent_a, agent_b])
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    dt = time.time() - t0
    return seed, r0, r1, dt

def main():
    tasks = [(100, "v25a", "v23"), (101, "v25a", "v23"), (102, "v25a", "v23"), (103, "v25a", "v23")]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        for res in executor.map(run_single_game, tasks):
            print(f"Seed {res[0]}: {res[1]:,.0f} vs {res[2]:,.0f} ({res[3]:.1f}s)", flush=True)

if __name__ == "__main__":
    main()
