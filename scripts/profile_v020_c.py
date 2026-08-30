import importlib.util
import os
import json
import numpy as np
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path).replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def profile_v020_c():
    agent_fn = load_agent("agents/v020_c_competitive_surgical.py")
    seeds = [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611]
    
    print("================================================================================")
    print("PROFILING V020-C (FROZEN CHAMPION) ACROSS 12 FRESH SEEDS (600-611)")
    print("================================================================================")
    
    daily_stats = {d: {
        "money": [], "unlocked_tiles": [], "planted_tiles": [], "empty_tiles": [],
        "hands": [], "melons": [], "strawberries": [], "wheat": [], "carrots": [],
        "water_actions": [], "harvest_actions": [], "plant_actions": [], "idle_worker_turns": []
    } for d in range(30)}
    
    final_banks = []
    
    for seed in seeds:
        os.environ["KAGGRICULTURE_SEED"] = str(seed)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([agent_fn, "random"])
        
        steps = env.steps
        final_banks.append(steps[-1][0]["reward"] or 0)
        
        for d in range(30):
            step_idx = d * 24 + 1
            obs = steps[step_idx][0]["observation"]
            f0 = obs["farms"][0]
            
            quads = len(f0.get("unlocked_quadrants", []))
            unlocked_t = quads * 25
            
            p_counts = {"MELON": 0, "STRAWBERRY": 0, "WHEAT": 0, "CARROT": 0}
            total_planted = 0
            empty_t = 0
            
            for r in range(len(f0["tiles"])):
                for c in range(len(f0["tiles"][r])):
                    t = f0["tiles"][r][c]
                    if t == "LOCKED": continue
                    elif isinstance(t, dict) and t.get("kind") == "PLANT":
                        crop = t.get("crop")
                        p_counts[crop] = p_counts.get(crop, 0) + 1
                        total_planted += 1
                    elif t is None:
                        empty_t += 1
                        
            daily_stats[d]["money"].append(f0["money"])
            daily_stats[d]["unlocked_tiles"].append(unlocked_t)
            daily_stats[d]["planted_tiles"].append(total_planted)
            daily_stats[d]["empty_tiles"].append(empty_t)
            daily_stats[d]["hands"].append(len(f0.get("hands", [])))
            daily_stats[d]["melons"].append(p_counts.get("MELON", 0))
            daily_stats[d]["strawberries"].append(p_counts.get("STRAWBERRY", 0))
            daily_stats[d]["wheat"].append(p_counts.get("WHEAT", 0))
            daily_stats[d]["carrots"].append(p_counts.get("CARROT", 0))
            
    print(f"\nMean Final Bank across 12 seeds: ${np.mean(final_banks):,.0f} (Min: ${np.min(final_banks):,.0f}, Max: ${np.max(final_banks):,.0f})")
    print("\nDAY-BY-DAY PROFILE (MEAN VALUES ACROSS 12 SEEDS):")
    print("Day | Money    | Unlocked | Planted | Empty | Hands | Melons | Strawberries | Wheat | Carrots")
    print("-" * 95)
    
    for d in range(30):
        print(f"{d:3d} | ${np.mean(daily_stats[d]['money']):7,.0f} | {np.mean(daily_stats[d]['unlocked_tiles']):8.1f} | {np.mean(daily_stats[d]['planted_tiles']):7.1f} | {np.mean(daily_stats[d]['empty_tiles']):5.1f} | {np.mean(daily_stats[d]['hands']):5.1f} | {np.mean(daily_stats[d]['melons']):6.1f} | {np.mean(daily_stats[d]['strawberries']):12.1f} | {np.mean(daily_stats[d]['wheat']):5.1f} | {np.mean(daily_stats[d]['carrots']):7.1f}")

if __name__ == "__main__":
    profile_v020_c()
