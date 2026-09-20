import os
import sys
sys.path.insert(0, os.path.abspath("."))
import collections
from kaggle_environments import make
from scripts.tournament_population import load_agent

CROPS_INFO = {
    "WHEAT": {"first": 2, "max_day": 4, "ongoing": False, "interval": 1},
    "CARROT": {"first": 3, "max_day": 5, "ongoing": False, "interval": 1},
    "TOMATO": {"first": 4, "max_day": 12, "ongoing": True, "interval": 2},
    "STRAWBERRY": {"first": 5, "max_day": 15, "ongoing": True, "interval": 2},
    "MELON": {"first": 6, "max_day": 8, "ongoing": False, "interval": 1}
}

def run_fert_ablation(seeds=[42, 101, 2024, 777, 9999]):
    print("=" * 60)
    print("ABLATION: YIELD-AWARE FERTILIZE")
    print("Investigating: fertilization timing relative to production events")
    print("=" * 60)
    
    base_agent = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py")
    
    total_fert = 0
    useful_fert = 0
    wasted_fert_redundant = 0
    wasted_fert_no_event = 0
    
    for seed in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([base_agent, "pass"])
        
        for step_idx, step_data in enumerate(env.steps[:-1]):
            obs = step_data[0]["observation"]
            action = step_data[0].get("action") or {}
            day = obs.get("day", step_idx // 24)
            farm = obs["farms"][0]
            tiles = farm["tiles"]
            units = [action.get("farmer")] + (action.get("hands") or [])
            positions = [farm["farmer"]] + farm["hands"]
            
            for u_idx, u_act in enumerate(units):
                if u_act and isinstance(u_act, list) and u_act[0] == "FERTILIZE":
                    total_fert += 1
                    if u_idx >= len(positions):
                        wasted_fert_no_event += 1
                        continue
                    pos = positions[u_idx]
                    t = tiles[pos[1]][pos[0]] if 0 <= pos[0] < 10 and 0 <= pos[1] < 10 else None
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        crop = t.get("crop")
                        c_info = CROPS_INFO.get(crop, {})
                        fert_until = t.get("fertilized_until_day", -1)
                        
                        # Check if already fertilized for >= day + 2
                        if fert_until >= day + 2:
                            wasted_fert_redundant += 1
                            continue
                            
                        # Check if production event happens in window [day, day+2]
                        planted = t.get("planted_day", 0)
                        ongoing = c_info.get("ongoing", False)
                        has_prod = False
                        
                        for target_day in range(day, day + 3):
                            if ongoing:
                                days_since = (target_day + 1) - planted - c_info["first"]
                                if days_since >= 0 and days_since % c_info["interval"] == 0:
                                    has_prod = True
                                    break
                            else:
                                age = target_day - planted
                                win_start = (c_info["max_day"] + 1) // 2
                                if win_start <= age <= c_info["max_day"]:
                                    has_prod = True
                                    break
                                    
                        if has_prod:
                            useful_fert += 1
                        else:
                            wasted_fert_no_event += 1
                    else:
                        wasted_fert_no_event += 1
                        
    print(f"Across {len(seeds)} seeds ({len(seeds)*720} steps):")
    print(f"Total FERTILIZE actions issued: {total_fert}")
    if total_fert > 0:
        print(f"Useful FERTILIZE (covers upcoming production event): {useful_fert} ({useful_fert/total_fert*100:.1f}%)")
        print(f"Wasted FERTILIZE (redundant / tile already fertilized): {wasted_fert_redundant} ({wasted_fert_redundant/total_fert*100:.1f}%)")
        print(f"Wasted FERTILIZE (no harvest/bonus event in 3-day window): {wasted_fert_no_event} ({wasted_fert_no_event/total_fert*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_fert_ablation()
