import os
import json
import numpy as np
from kaggle_environments import make
import importlib.util

def load_agent(agent_file):
    spec = importlib.util.spec_from_file_location("agent", agent_file)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return agent_module

agent_c = load_agent("agents/v018_d_subsistence.py")
seeds = [1, 2, 3, 4, 5]

print("===============================")
print("V018-D Fallback Sweep")
print("===============================")

for mode in ["WHEAT_ONLY", "EV_BASED"]:
    for trigger in [5, 10, 15]:
        os.environ['V018_D_EMPTY_LAND_TRIGGER'] = str(trigger)
        os.environ['V018_D_FALLBACK_MODE'] = mode
        banks = []
        plants = []
        
        for seed in seeds:
            os.environ["KAGGRICULTURE_SEED"] = str(seed)
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
            
            def wrapper(obs):
                try:
                    action = agent_c.agent(obs)
                    agent_c.MetricsTracker.save(
                        obs.get("player"), obs.get("step"), obs.get("farms")[obs.get("player")].get("money")
                    )
                    return action
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise e
                    
            env.run([wrapper, "random"])
            
            metrics_path = f"experiments/metrics/game_{seed}_p0.json"
            if os.path.exists(metrics_path):
                with open(metrics_path) as mf:
                    m = json.load(mf)
                    banks.append(m["economy"]["final_money"])
                    plants.append(sum(c["planted"] for c in m.get("crops", {}).values()))
                    
        print(f"Mode={mode}, Trigger={trigger}: Mean Bank=${np.mean(banks):.2f} (Plants: {np.mean(plants):.1f})")
