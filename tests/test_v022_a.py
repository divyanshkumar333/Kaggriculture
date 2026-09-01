import os
import importlib.util
from kaggle_environments import make

def load_agent(agent_file):
    spec = importlib.util.spec_from_file_location("dynamic_agent", agent_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def test_smoke_v022_a():
    v022_a = load_agent("agents/v022_a_replay_opening.py")
    env = make("kaggriculture", configuration={"episodeSteps": 100}, debug=True)
    env.run([v022_a, "random"])
    
    final_step = env.steps[-1]
    assert final_step[0]["status"] == "DONE"
    print(f"Smoke test 100 steps reward: {final_step[0]['reward']}")

def test_v022_a_vs_v020_c():
    v022_a = load_agent("agents/v022_a_replay_opening.py")
    v020_c = load_agent("agents/v020_c_competitive_surgical.py")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
    env.run([v022_a, v020_c])
    
    final_step = env.steps[-1]
    p0_m = final_step[0]["observation"]["farms"][0]["money"]
    p1_m = final_step[0]["observation"]["farms"][1]["money"]
    print(f"\n720 steps Seed 42 | V022-A (P0): ${p0_m:,} vs V020-C (P1): ${p1_m:,}")

if __name__ == "__main__":
    test_smoke_v022_a()
    test_v022_a_vs_v020_c()
