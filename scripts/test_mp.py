import multiprocessing as mp
import time
from kaggle_environments import make

def run_env(seed):
    import importlib.util
    spec = importlib.util.spec_from_file_location("mod_v25", "agents/v025_a_aggressive_cows.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    v25_agent = mod.agent

    spec_g = importlib.util.spec_from_file_location("mod_v23", "agents/v023_g_capital_optimizer.py")
    mod_g = importlib.util.module_from_spec(spec_g)
    spec_g.loader.exec_module(mod_g)
    v23_agent = mod_g.agent

    t0 = time.time()
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([v25_agent, v23_agent])
    dt = time.time() - t0
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    return seed, r0, r1, dt

def main():
    seeds = [100, 101, 102, 103]
    with mp.Pool(processes=4) as pool:
        for res in pool.imap_unordered(run_env, seeds):
            print(f"Seed {res[0]}: {res[1]} vs {res[2]} in {res[3]:.2f}s", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    main()
