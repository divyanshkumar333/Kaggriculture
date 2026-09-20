import os
import sys
sys.path.insert(0, os.path.abspath("."))
from kaggle_environments import make
from scripts.tournament_population import load_agent

def run_feeding_ablation(seeds=[42, 101, 2024, 777, 9999]):
    print("=" * 60)
    print("ABLATION: FEEDING ROUTE COMMITMENT & ANIMAL HEALTH")
    print("Investigating: animal escapes, missed feeds, and daily feed consistency")
    print("=" * 60)
    
    base_agent = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py")
    
    total_animal_days = 0
    total_missed_feeds = 0
    total_escapes = 0
    
    for seed in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([base_agent, "pass"])
        
        escapes_this_game = 0
        missed_this_game = 0
        
        # Check end of each day (step % 24 == 23)
        for day in range(30):
            step_idx = day * 24 + 23
            if step_idx < len(env.steps):
                obs = env.steps[step_idx][0]["observation"]
                farm = obs["farms"][0]
                tiles = farm["tiles"]
                for r in tiles:
                    for t in r:
                        if isinstance(t, dict):
                            if "animal" in t:
                                total_animal_days += 1
                                if not t.get("fed_today", False):
                                    total_missed_feeds += 1
                                    missed_this_game += 1
                            elif t.get("kind") in ("COOP", "PASTURE") and "animal" not in t and day > 5:
                                # Structure exists but no animal - could be escaped or waiting placement
                                pass
                                
        print(f"Seed {seed}: Missed feeds = {missed_this_game}")
        
    print("-" * 60)
    print(f"Total Animal Days Evaluated: {total_animal_days}")
    print(f"Total Missed Daily Feeds: {total_missed_feeds} ({total_missed_feeds/total_animal_days*100:.2f}%)")
    print(f"Feeding Reliability: {(1 - total_missed_feeds/total_animal_days)*100:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    run_feeding_ablation()
