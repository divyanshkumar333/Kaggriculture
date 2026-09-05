import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

a_v026_a = load_agent("agents/v026_a_il_hybrid.py")
a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 404}, debug=False)
for step in range(720):
    act0 = a_v026_a(env.state[0].observation)
    act1 = a_v025(env.state[1].observation)
    env.step([act0, act1])
    if step in [24*5, 24*10, 24*15, 24*20, 24*25]:
        d = step // 24
        f0 = env.state[0].observation.farms[0]
        f1 = env.state[1].observation.farms[1]
        print(f"Day {d:2d} | V026-A: Money=${f0['money']:6.0f}, Quads={len(f0['unlocked_quadrants'])} | V025-A: Money=${f1['money']:6.0f}, Quads={len(f1['unlocked_quadrants'])}")
