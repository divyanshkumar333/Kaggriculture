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

print("Hour-by-hour plant & seed audit on Days 10-18:")
for day in range(10, 19):
    for h in [0, 12, 23]:
        step_idx = day * 24 + h
        obs = env.steps[step_idx][0]["observation"]
        f = obs["farms"][0]
        p = obs["private"]
        plants = []
        for r in range(10):
            for c in range(10):
                t = f["tiles"][r][c]
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    plants.append((c, r, t.get("crop"), t.get("yield_units"), t.get("watered_today"), t.get("consecutive_unwatered")))
        weeds = sum(1 for r in range(10) for c in range(10) if isinstance(f["tiles"][r][c], dict) and f["tiles"][r][c].get("kind") == "WEED")
        seeds = p["seeds"]
        print(f"Day {day:2d} H{h:2d} | Seeds: {seeds} | Plants({len(plants)}): {plants[:2]} | Weeds: {weeds}")
