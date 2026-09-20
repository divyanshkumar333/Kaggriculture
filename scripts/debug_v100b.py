from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, ".")
spec = importlib.util.spec_from_file_location("v100b", "agents/v100b_gm_fixed_opening.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make("kaggriculture", configuration={"episodeSteps": 97, "randomSeed": 8100}, debug=False)

def v100b_agent(obs, cfg):
    me = obs["farms"][0]
    priv = obs["private"]
    shed = priv["shed"]
    tiles = me["tiles"]
    animals = [(c,r,t.get("animal"),t.get("fed_today"),t.get("consecutive_unfed"))
               for r in range(10) for c in range(10)
               if isinstance(t := tiles[r][c], dict) and t.get("kind") in ("COOP","PASTURE")]
    if obs["day"] <= 5 and obs["hour"] == 0:
        print(f"Day {obs[\"day\"]}: money={me[\"money\"]} wheat={shed.get(\"WHEAT\",0)} animals={len(animals)} {animals[:3]}")
    return mod.agent(obs)

env.run([v100b_agent, "random"])
final = env.steps[-1]
print("Final P0 reward:", final[0].reward)
