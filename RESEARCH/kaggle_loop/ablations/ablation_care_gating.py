import os
import sys
sys.path.insert(0, os.path.abspath("."))
import collections
from kaggle_environments import make
from scripts.tournament_population import load_agent

def run_care_ablation(seeds=[42, 101, 2024, 777, 9999]):
    print("=" * 60)
    print("ABLATION: CARE GATING")
    print("Investigating: care always vs care only after fed vs care economically useful")
    print("=" * 60)
    
    # We inspect how the base agent performs CARE
    base_agent = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py")
    
    # Measure wasted CARE operations across seeds in the baseline agent
    wasted_care_unfed = 0
    wasted_care_overflow = 0
    useful_care = 0
    total_care = 0
    
    for seed in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        # Run against pass
        env.run([base_agent, "pass"])
        
        # Step through replay to check CARE preconditions
        for step_idx, step_data in enumerate(env.steps[:-1]):
            obs = step_data[0]["observation"]
            action = step_data[0].get("action") or {}
            farm = obs["farms"][0]
            tiles = farm["tiles"]
            units = [action.get("farmer")] + (action.get("hands") or [])
            positions = [farm["farmer"]] + farm["hands"]
            
            for u_idx, u_act in enumerate(units):
                if u_act and isinstance(u_act, list) and u_act[0] == "CARE":
                    total_care += 1
                    if u_idx >= len(positions):
                        wasted_care_unfed += 1
                        continue
                    pos = positions[u_idx]
                    t = tiles[pos[1]][pos[0]] if 0 <= pos[0] < 10 and 0 <= pos[1] < 10 else None
                    if isinstance(t, dict) and "animal" in t:
                        is_fed = t.get("fed_today", False)
                        yield_held = t.get("yield_units", 0)
                        pending_bonus = t.get("pending_care_bonus", 0)
                        
                        if not is_fed:
                            wasted_care_unfed += 1
                        elif yield_held + pending_bonus >= 5: # max_held is 6, base is 1, so bonus >= 5 hits cap
                            wasted_care_overflow += 1
                        else:
                            useful_care += 1
                            
    print(f"Across {len(seeds)} seeds ({len(seeds)*720} steps):")
    print(f"Total CARE actions issued: {total_care}")
    print(f"Useful CARE (fed + headroom): {useful_care} ({useful_care/total_care*100:.1f}%)")
    print(f"Wasted CARE (animal NOT fed yet today): {wasted_care_unfed} ({wasted_care_unfed/total_care*100:.1f}%)")
    print(f"Wasted CARE (animal bonus at max_held cap): {wasted_care_overflow} ({wasted_care_overflow/total_care*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_care_ablation()
