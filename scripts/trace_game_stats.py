import importlib.util
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v022_b = load_agent("agents/v022_b_dynamic_labor.py")
v020_c = load_agent("agents/v020_c_competitive_surgical.py")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
env.run([v022_b, v020_c])

print(" Day |   Money   | Quads | Hands | Cows | Sheep | Plants | WheatShed | MilkShed | WoolShed | FertShed")
print("-" * 95)

for day in range(30):
    step_idx = day * 24
    obs = env.steps[step_idx][0]["observation"]
    f = obs["farms"][0]
    p = obs["private"]
    cows = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "COW")
    sheep = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "SHEEP")
    plants = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("kind") == "PLANT")
    quads = len(f["unlocked_quadrants"])
    hands = len(f["hands"])
    money = f["money"]
    wheat = p["shed"].get("WHEAT", 0)
    milk = p["shed"].get("MILK", 0)
    wool = p["shed"].get("WOOL", 0)
    fert = p["shed"].get("FERTILIZER", 0)
    print(f"{day:4d} | ${money:8.0f} | {quads:5d} | {hands:5d} | {cows:4d} | {sheep:5d} | {plants:6d} | {wheat:9d} | {milk:8d} | {wool:8d} | {fert:8d}")

final_s = env.steps[-1]
print(f"FINAL RESULT: P0 (V022-B) = ${final_s[0].reward:.0f}, P1 (V020-C) = ${final_s[1].reward:.0f}")
