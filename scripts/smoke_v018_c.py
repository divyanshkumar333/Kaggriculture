import json
import statistics
import sys
import numpy as np
from kaggle_environments import make

import importlib.util

import importlib.util
import os

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_module", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return agent_module

agent_c = load_agent("agents/v018_c_inventory_pacing_v2.py")

seeds = [1, 2, 3, 4, 5]
results = []

for seed in seeds:
    os.environ["KAGGRICULTURE_SEED"] = str(seed)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    
    # Use a wrapper to save metrics
    def wrapper(obs):
        try:
            action = agent_c.agent(obs)
            if obs.step == 719:
                agent_c.MetricsTracker.save(
                    obs.player,
                    obs.step,
                    obs.farms[obs.player]["money"],
                    obs.private["shed"],
                    [],
                    obs.day
                )
            return action
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
        
    # Run game
    steps = env.run([wrapper, "random"])
    
    # Extract metrics
    p0_reward = steps[-1][0].reward or 0
    
    metrics_path = f"experiments/metrics/game_{seed}_p0.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            m = json.load(f)
    else:
        m = {}
            
    crops = m.get("crops", {})
    workers = m.get("workers", {})
    farmer = m.get("farmer", {})
    econ = m.get("economy", {})
    
    total_rev = m.get("market", {}).get("revenue", 0)
    seed_spend = econ.get("seed_spending", 0)
    
    useful_acts = workers.get("useful_actions", 0) + farmer.get("useful_actions", 0)
    move_acts = workers.get("move_actions", 0) + farmer.get("move_actions", 0)
    idle = workers.get("idle_actions", 0) + farmer.get("idle_actions", 0)
    
    plant_count = sum(c.get("planted", 0) for c in crops.values())
    harvest_count = sum(c.get("harvested", 0) for c in crops.values())
    crop_deaths = sum(c.get("deaths", 0) for c in crops.values())
    water_misses = sum(c.get("water_misses", 0) for c in crops.values())
    
    pipeline_values = m.get("pipeline_values", {})
    c1_rejections = m.get("c1_rejections", 0)
    
    results.append({
        "seed": seed,
        "bank": p0_reward,
        "revenue": total_rev,
        "seed_spend": seed_spend,
        "useful_actions": useful_acts,
        "move_actions": move_acts,
        "idle_actions": idle,
        "plant_count": plant_count,
        "harvest_count": harvest_count,
        "crop_deaths": crop_deaths,
        "water_misses": water_misses,
        "pipeline_values": pipeline_values,
        "c1_rejections": c1_rejections
    })
    
    pass

# Aggregate
print("===============================")
print("V018-C C1 Smoke Test Results (5 Games)")
print("===============================")

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
print(f"Mean C1 Rejections: {np.mean([r['c1_rejections'] for r in results]):.1f}")

# Average pipeline values
all_pipelines = {c: [] for c in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]}
for r in results:
    for c, vals in r["pipeline_values"].items():
        all_pipelines[c].extend(vals)

print("\nMean Pipeline Values observed during evaluation:")
for c, vals in all_pipelines.items():
    if vals:
        print(f"  {c}: {np.mean(vals):.2f} (max: {max(vals):.2f})")
    else:
        print(f"  {c}: N/A")
