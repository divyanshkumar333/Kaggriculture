import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

a_v026_a = load_agent("agents/v026_a_il_hybrid.py")
a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

env = make("kaggriculture", configuration={"episodeSteps": 24*6, "seed": 404}, debug=False)
for step in range(24*6):
    obs0 = env.state[0].observation
    obs1 = env.state[1].observation
    act0 = a_v026_a(obs0)
    act1 = a_v025(obs1)
    if act0.get("market") or act1.get("market"):
        d = step // 24
        h = step % 24
        print(f"Step {step:3d} (D{d}H{h:02d}):")
        if act0.get("market"): print(f"  V026-A Market: {act0['market']}")
        if act1.get("market"): print(f"  V025-A Market: {act1['market']}")
    env.step([act0, act1])
