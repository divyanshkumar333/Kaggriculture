import importlib.util
from kaggle_environments import make
import pandas as pd

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def trace():
    v022_a = load_agent("agents/v022_a_replay_opening.py")
    v020_c = load_agent("agents/v020_c_competitive_surgical.py")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
    env.run([v022_a, v020_c])
    
    steps = env.steps
    print("=== SEED 42 TRACE OF V022-A ===")
    for day in range(30):
        day_steps = steps[day*24 : (day+1)*24]
        s0 = day_steps[0][0]["observation"]
        s_end = day_steps[-1][0]["observation"]
        
        p0_start = s0["farms"][0]
        p0_end = s_end["farms"][0]
        
        # Count tiles
        tiles = p0_end["tiles"]
        plants = {}
        animals = {}
        empty = 0
        weeds = 0
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if t is None: empty += 1
                elif isinstance(t, dict):
                    k = t.get("kind")
                    if k == "WEED": weeds += 1
                    elif k == "PLANT":
                        cr = t.get("crop")
                        plants[cr] = plants.get(cr, 0) + 1
                    elif k in ["PASTURE", "COOP"]:
                        an = t.get("animal")
                        if an: animals[an] = animals.get(an, 0) + 1
                        else: animals[f"EMPTY_{k}"] = animals.get(f"EMPTY_{k}", 0) + 1
                        
        print(f"Day {day:2d} | Money: ${p0_start['money']:>6,.0f} -> ${p0_end['money']:>6,.0f} | Quads: {len(p0_end['unlocked_quadrants'])} | Hands: {len(p0_end['hands'])} | Animals: {animals} | Plants: {plants} | Weeds: {weeds}")

if __name__ == "__main__":
    trace()
