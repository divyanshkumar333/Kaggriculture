import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

a_v026_a = load_agent("agents/v026_a_il_hybrid.py")
a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

SEEDS = [42, 101, 202, 303, 404, 505]
print("=== Head-to-Head: V026-A vs V025-A ===")
for s in SEEDS:
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([a_v026_a, a_v025])
    m0 = env1.steps[-1][0]["observation"]["farms"][0]["money"]
    m1 = env1.steps[-1][0]["observation"]["farms"][1]["money"]

    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env2.run([a_v025, a_v026_a])
    m0_rev = env2.steps[-1][0]["observation"]["farms"][0]["money"]
    m1_rev = env2.steps[-1][0]["observation"]["farms"][1]["money"]

    print(f"Seed {s:3d} | As P0: V026-A={m0:,.0f} vs V025={m1:,.0f} ({m0-m1:+,.0f}) | As P1: V026-A={m1_rev:,.0f} vs V025={m0_rev:,.0f} ({m1_rev-m0_rev:+,.0f})")
