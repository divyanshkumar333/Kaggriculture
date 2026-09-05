"""
Current Meta Miner: Download and parse Kaggle episodes across ladder
"""

import subprocess
import json
import os
import glob
import pandas as pd
import numpy as np

EPISODES_DIR = "kaggle_episodes"
os.makedirs(EPISODES_DIR, exist_ok=True)

def fetch_submission_episodes(submission_id):
    cmd = [r".venv\Scripts\kaggle.exe", "competitions", "episodes", str(submission_id), "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    if len(lines) <= 1:
        return []
    episodes = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) >= 5:
            ep_id = parts[0].strip()
            state = parts[3].strip()
            ep_type = parts[4].strip()
            if "COMPLETED" in state and "PUBLIC" in ep_type:
                episodes.append(ep_id)
    return episodes

def download_episode(ep_id):
    target = os.path.join(EPISODES_DIR, f"episode-{ep_id}-replay.json")
    if os.path.exists(target):
        return target
    cmd = [r".venv\Scripts\kaggle.exe", "competitions", "replay", str(ep_id), "-p", EPISODES_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(target):
        return target
    return None

def parse_replay_summary(replay_path):
    try:
        with open(replay_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {replay_path}: {e}")
        return None

    info = data.get("info", {})
    team_names = info.get("TeamNames", ["Unknown", "Unknown"])
    agents_info = info.get("Agents", [{}, {}])
    steps = data.get("steps", [])
    if not steps:
        return None
    
    last_step = steps[-1]
    r0 = float(last_step[0].get("reward", 0))
    r1 = float(last_step[1].get("reward", 0))
    
    # Extract telemetry at key checkpoints: D0, D5, D8, D10, D15, D20, D25, D30 (Step 0, 120, 192, 240, 360, 480, 600, 719)
    checkpoints = {0: 0, 5: 120, 8: 192, 10: 240, 15: 360, 20: 480, 25: 600, 30: 719}
    
    telemetry = {0: {}, 1: {}}
    for p in [0, 1]:
        telemetry[p]["team"] = team_names[p] if len(team_names) > p else "Unknown"
        telemetry[p]["final_reward"] = r0 if p == 0 else r1
        telemetry[p]["won"] = (r0 > r1) if p == 0 else (r1 > r0)
        telemetry[p]["checkpoints"] = {}
        
    for d, step_idx in checkpoints.items():
        if step_idx < len(steps):
            step_data = steps[step_idx]
            # Observation is in step_data[0]['observation']
            obs = step_data[0].get("observation", {})
            farms = obs.get("farms", [])
            for p in [0, 1]:
                if len(farms) > p:
                    farm = farms[p]
                    money = farm.get("money", 0)
                    hands = len(farm.get("hands", []))
                    unlocked_q = len(farm.get("unlocked_quadrants", []))
                    tiles = farm.get("tiles", [])
                    
                    cows = 0
                    sheep = 0
                    pastures = 0
                    coops = 0
                    plants = {"WHEAT": 0, "CARROT": 0, "TOMATO": 0, "STRAWBERRY": 0, "MELON": 0}
                    weeds = 0
                    
                    for row in tiles:
                        for tile in row:
                            if isinstance(tile, dict):
                                kind = tile.get("kind")
                                if kind == "PASTURE":
                                    pastures += 1
                                    animal = tile.get("animal")
                                    if animal == "COW": cows += 1
                                    elif animal == "SHEEP": sheep += 1
                                elif kind == "COOP":
                                    coops += 1
                                elif kind == "PLANT":
                                    crop = tile.get("crop")
                                    if crop in plants:
                                        plants[crop] += 1
                                elif kind == "WEED":
                                    weeds += 1
                                    
                    telemetry[p]["checkpoints"][d] = {
                        "money": money,
                        "workers": hands + 1,
                        "quadrants": unlocked_q,
                        "cows": cows,
                        "sheep": sheep,
                        "pastures": pastures,
                        "strawberries": plants["STRAWBERRY"],
                        "wheat": plants["WHEAT"],
                        "melons": plants["MELON"],
                        "tomatoes": plants["TOMATO"],
                        "carrots": plants["CARROT"],
                        "weeds": weeds
                    }
                    
    return {
        "replay_file": os.path.basename(replay_path),
        "episode_id": info.get("EpisodeId"),
        "seed": info.get("seed"),
        "player_0": telemetry[0],
        "player_1": telemetry[1]
    }

if __name__ == "__main__":
    sub_ids = [56018982, 56026365, 55946810]
    all_episodes = []
    for sid in sub_ids:
        eps = fetch_submission_episodes(sid)
        print(f"Submission {sid}: found {len(eps)} public completed episodes")
        all_episodes.extend(eps)
        
    all_episodes = list(set(all_episodes))
    print(f"Total unique episodes to download: {len(all_episodes)}")
    
    # Download top 25 recent episodes
    downloaded = []
    for ep in all_episodes[:30]:
        p = download_episode(ep)
        if p:
            downloaded.append(p)
            
    print(f"Successfully downloaded {len(downloaded)} episodes")
