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
results = []

os.environ['V018_D_EMPTY_LAND_TRIGGER'] = '10'
os.environ['V018_D_FALLBACK_MODE'] = 'WHEAT_ONLY'

for seed in seeds:
    os.environ["KAGGRICULTURE_SEED"] = str(seed)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    
    # Use a wrapper to save metrics
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
            
    steps = env.run([wrapper, "starter"])
    
    metrics_path = f"experiments/metrics/game_{seed}_p0.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            m = json.load(f)
            
            econ = m.get("economy", {})
            revenue = econ.get("total_revenue", 0)
            seed_spend = econ.get("seed_spending", 0)
            
            useful = m.get("efficiency", {}).get("useful_actions_total", 0)
            plants = sum(c.get("planted", 0) for c in m.get("crops", {}).values())
            harvests = sum(c.get("harvested", 0) for c in m.get("crops", {}).values())
            deaths = sum(c.get("deaths", 0) for c in m.get("crops", {}).values())
            misses = m.get("water", {}).get("misses", 0)
            
            move_acts = m.get("farmer", {}).get("movement_actions", 0) + m.get("workers", {}).get("movement_actions", 0)
            idle = m.get("farmer", {}).get("idle_turns", 0) + m.get("workers", {}).get("idle_turns", 0)
            
            results.append({
                "seed": seed,
                "bank": econ.get("final_money", 0),
                "revenue": revenue,
                "seed_spend": seed_spend,
                "useful_actions": useful,
                "plant_count": plants,
                "harvest_count": harvests,
                "crop_deaths": deaths,
                "water_misses": misses,
                "move_actions": move_acts,
                "idle_actions": idle
            })

print("===============================")
print("V018-D Smoke Test Results (5 Games)")
print("===============================")
if results:
    banks = [r["bank"] for r in results]
    print(f"Mean Bank: ${np.mean(banks):.2f}")
    print(f"Mean Revenue: ${np.mean([r['revenue'] for r in results]):.2f}")
    print(f"Mean Seed Spend: ${np.mean([r['seed_spend'] for r in results]):.2f}")
    print(f"Mean Useful Actions: {np.mean([r['useful_actions'] for r in results]):.1f}")
    print(f"Mean Plant Count: {np.mean([r['plant_count'] for r in results]):.1f}")
    print(f"Mean Harvest Count: {np.mean([r['harvest_count'] for r in results]):.1f}")
    print(f"Mean Crop Deaths: {np.mean([r['crop_deaths'] for r in results]):.1f}")
    print(f"Mean Water Misses: {np.mean([r['water_misses'] for r in results]):.1f}")
    print(f"Mean Movement: {np.mean([r['move_actions'] for r in results]):.1f}")
    print(f"Mean Idle: {np.mean([r['idle_actions'] for r in results]):.1f}")
else:
    print("No results found.")
