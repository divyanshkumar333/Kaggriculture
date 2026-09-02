"""
Compare V022-C Game Telemetry vs Mined $162k Replay (Episode 103388734)
"""
import importlib.util
import json
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v022_c = load_agent("agents/v022_c_market_batching.py")

# Run V022-C solo/vs random to trace macroeconomic telemetry
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
env.run([v022_c, "random"])

CHECKPOINTS = [0, 5, 6, 10, 15, 20, 25, 29]

print("="*105)
print(f"{'CHECKPOINT':<10} | {'CASH':<8} | {'HANDS':<5} | {'ANIM':<5} | {'COW':<4} | {'SHEEP':<5} | {'QUADS':<5} | {'PLANTS':<6} | {'WHEAT':<5} | {'STRAW':<5} | {'FERT':<5} | {'MILK':<5} | {'WOOL':<5}")
print("="*105)

checkpoint_data = []

for d in CHECKPOINTS:
    step_idx = d * 24 + 23
    obs = env.steps[step_idx][0]["observation"]
    f = obs["farms"][0]
    p = obs["private"]
    
    cash = f["money"]
    hands = len(f["hands"])
    quads = len(f["unlocked_quadrants"])
    shed = p["shed"]
    tiles = f["tiles"]
    
    cows = 0
    sheep = 0
    plants = 0
    wheat_plants = 0
    straw_plants = 0
    
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if isinstance(t, dict):
                k = t.get("kind")
                if k in ["COOP", "PASTURE"]:
                    an = t.get("animal")
                    if an == "COW": cows += 1
                    elif an == "SHEEP": sheep += 1
                elif k == "PLANT":
                    plants += 1
                    cr = t.get("crop")
                    if cr == "WHEAT": wheat_plants += 1
                    elif cr == "STRAWBERRY": straw_plants += 1
                    
    animals = cows + sheep
    fert = shed.get("FERTILIZER", 0)
    milk = shed.get("MILK", 0)
    wool = shed.get("WOOL", 0)
    
    print(f"Day {d:2d} (H23)  | ${cash:7.0f} | {hands:5d} | {animals:5d} | {cows:4d} | {sheep:5d} | {quads:5d} | {plants:6d} | {wheat_plants:5d} | {straw_plants:5d} | {fert:5d} | {milk:5d} | {wool:5d}")
    checkpoint_data.append({
        "day": d,
        "cash": cash,
        "hands": hands,
        "animals": animals,
        "cows": cows,
        "sheep": sheep,
        "quads": quads,
        "plants": plants,
        "wheat_plants": wheat_plants,
        "straw_plants": straw_plants,
        "fert_shed": fert,
        "milk_shed": milk,
        "wool_shed": wool
    })

with open("scratch/replay_telemetry_checkpoints.json", "w") as f:
    json.dump(checkpoint_data, f, indent=2)

print("\nCheckpoint telemetry saved to scratch/replay_telemetry_checkpoints.json")
