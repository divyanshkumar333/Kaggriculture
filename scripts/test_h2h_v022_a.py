import importlib.util
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def test_h2h_seed42():
    v022_a = load_agent("agents/v022_a_replay_opening.py")
    v020_c = load_agent("agents/v020_c_competitive_surgical.py")
    
    print("=== MATCH 1: V022-A (P0) vs V020-C (P1) | Seed 42 ===")
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
    env1.run([v022_a, v020_c])
    p0_m = env1.steps[-1][0]["observation"]["farms"][0]["money"]
    p1_m = env1.steps[-1][0]["observation"]["farms"][1]["money"]
    winner = "V022-A" if p0_m > p1_m else "V020-C"
    print(f"Result: V022-A: ${p0_m:,} | V020-C: ${p1_m:,} | Winner: {winner}")

    print("\n=== MATCH 2: V020-C (P0) vs V022-A (P1) | Seed 42 ===")
    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
    env2.run([v020_c, v022_a])
    p0_m = env2.steps[-1][0]["observation"]["farms"][0]["money"]
    p1_m = env2.steps[-1][0]["observation"]["farms"][1]["money"]
    winner = "V022-A" if p1_m > p0_m else "V020-C"
    print(f"Result: V020-C: ${p0_m:,} | V022-A: ${p1_m:,} | Winner: {winner}")

if __name__ == "__main__":
    test_h2h_seed42()
