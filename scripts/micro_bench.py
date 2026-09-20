"""Micro-benchmark: time a single game, then 4 sequential games. Measure wall-clock, peak RAM."""
import time, os, sys, tracemalloc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def run_one_game(agent_a_path, agent_b_path, seed):
    from kaggle_environments import make
    import importlib.util
    
    def load_agent(path):
        spec = importlib.util.spec_from_file_location("_agent", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.agent

    agent_a = load_agent(agent_a_path)
    agent_b = load_agent(agent_b_path)
    env = make("kaggriculture", configuration={"episodeSteps": 721, "randomSeed": seed}, debug=False)
    
    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (farm.get("hands") or [])], "market": []}

    env.run([lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg),
             lambda obs, cfg, _b=agent_b: _safe(_b, obs, cfg)])
    final = env.steps[-1]
    return float(final[0].reward or 0), float(final[1].reward or 0)

def main():
    agent_a = os.path.join(ROOT, "agents", "v057_generalized_spoiler.py")
    agent_b = os.path.join(ROOT, "main.py")
    
    print("=== MICRO-BENCHMARK ===")
    print(f"A: {os.path.basename(agent_a)}")
    print(f"B: {os.path.basename(agent_b)}")
    
    # --- Single game ---
    tracemalloc.start()
    t0 = time.perf_counter()
    r0, r1 = run_one_game(agent_a, agent_b, 11000)
    t1 = time.perf_counter()
    _, peak1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    single_time = t1 - t0
    print(f"\n1 game:  {single_time:.1f}s  |  Peak RAM: {peak1/1024/1024:.0f} MB  |  Score: {r0:.0f} vs {r1:.0f}")
    
    # --- 4 sequential games ---
    tracemalloc.start()
    t0 = time.perf_counter()
    for seed in [11000, 11001, 11002, 11003]:
        ra, rb = run_one_game(agent_a, agent_b, seed)
        print(f"  seed {seed}: {ra:.0f} vs {rb:.0f}")
    t4 = time.perf_counter()
    _, peak4 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    quad_time = t4 - t0
    sec_per_game = quad_time / 4
    games_per_hour = 3600 / sec_per_game
    
    print(f"\n4 games: {quad_time:.1f}s  |  Peak RAM: {peak4/1024/1024:.0f} MB")
    print(f"  sec/game:           {sec_per_game:.1f}")
    print(f"  games/hour:         {games_per_hour:.0f}")
    print(f"  est 128 games:      {128 * sec_per_game / 60:.0f} min")
    print(f"  est 384 games:      {384 * sec_per_game / 60:.0f} min")
    print(f"  est 128 seed-blocks (256 games): {256 * sec_per_game / 60:.0f} min")

if __name__ == "__main__":
    main()
