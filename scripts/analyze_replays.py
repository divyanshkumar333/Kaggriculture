import json
import glob
import os

def analyze_replay(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    steps = data.get("steps", [])
    if not steps:
        return
        
    # Get final rewards
    final_step = steps[-1]
    rewards = [s.get("reward", 0) for s in final_step]
    
    # Analyze agent 0 and agent 1
    for player in [0, 1]:
        print(f"--- Player {player} (Reward: {rewards[player]}) ---")
        for step_idx in [0, 72, 144, 240, 719]: # Day 0, Day 3, Day 6, Day 10, End
            if step_idx >= len(steps):
                break
            obs = steps[step_idx][0].get("observation", {})
            farms = obs.get("farms", [])
            if not farms or len(farms) <= player:
                continue
            farm = farms[player]
            money = farm.get("money", 0)
            
            # count tiles
            tiles = farm.get("tiles", [])
            plants = {}
            animals = {}
            for row in tiles:
                for tile in row:
                    if isinstance(tile, dict):
                        if tile.get("kind") == "PLANT":
                            c = tile.get("crop", "unknown")
                            plants[c] = plants.get(c, 0) + 1
                        elif tile.get("kind") in ["COOP", "PASTURE"] and "animal" in tile:
                            a = tile.get("animal", "unknown")
                            animals[a] = animals.get(a, 0) + 1
            
            print(f"Step {step_idx:3d} (Day {step_idx//24}): Money=${money:<5} Plants={plants} Animals={animals}")
        print()

if __name__ == "__main__":
    replays = glob.glob("episode-*-replay.json")
    for r in replays:
        print(f"=== {r} ===")
        analyze_replay(r)
