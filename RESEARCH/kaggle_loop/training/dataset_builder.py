import glob
import json
import numpy as np
import os
from features import extract_features

def build_datasets():
    replays = glob.glob("episode-*.json")
    if not replays:
        print("No replays found in root directory!")
        return

    # For dataset
    X_train, y_train = [], []
    X_val, y_val = [], []
    
    # Simple split: first 6 for train, last 2 for val
    train_replays = replays[:-2]
    val_replays = replays[-2:]
    
    def process_replay(r_path, X_list, y_list):
        print(f"Processing {r_path}")
        with open(r_path, "r") as f:
            data = json.load(f)
            
        steps = data.get("steps", [])
        if not steps: return
        
        final_step = steps[-1]
        p0_reward = final_step[0].get("reward", 0)
        p1_reward = final_step[1].get("reward", 0)
        
        # Binary classification for value model (1 if win, 0 if lose)
        p0_win = 1 if p0_reward > p1_reward else 0
        p1_win = 1 if p1_reward > p0_reward else 0
        
        # We also need labels for Opponent Classifier (MELON vs STRAWBERRY vs COW)
        # We can extract the final count of opponent's items at day 10, but for simplicity,
        # we will heuristically label the replay based on max planted crops in the game.
        
        for player, win_label in [(0, p0_win), (1, p1_win)]:
            # For each player, view the game from their perspective
            opp_idx = 1 - player
            
            # Determine opponent archetype heuristically from full replay
            opp_max_melons = 0
            opp_max_livestock = 0
            for step_idx, step in enumerate(steps):
                obs = step[0].get("observation", {})
                if not obs: obs = step[0]
                if isinstance(obs, str):
                    try: obs = json.loads(obs)
                    except: continue
                    
                farms = obs.get("farms", [])
                if len(farms) < 2: continue
                opp_farm = farms[opp_idx]
                
                m_count, l_count = 0, 0
                for row in opp_farm.get("tiles", []):
                    for tile in row:
                        if isinstance(tile, dict):
                            if tile.get("crop") == "MELON": m_count += 1
                            elif tile.get("kind") in ["COOP", "PASTURE"]: l_count += 1
                opp_max_melons = max(opp_max_melons, m_count)
                opp_max_livestock = max(opp_max_livestock, l_count)
                
            if opp_max_melons >= 8: opp_archetype = 0 # MELON_RUSH
            elif opp_max_livestock >= 2: opp_archetype = 1 # LIVESTOCK_RUSH
            else: opp_archetype = 2 # STRAWBERRY / BALANCED
            
            # Now build step-by-step features (only up to day 28 to avoid liquidation noise)
            for step_idx in range(0, min(len(steps), 700), 5):
                step = steps[step_idx]
                obs = step[0].get("observation", {})
                if not obs: obs = step[0]
                if isinstance(obs, str):
                    try: obs = json.loads(obs)
                    except: continue
                    
                feats = extract_features(obs, player)
                if feats is not None:
                    # Target: [Win_Label, Opponent_Archetype]
                    X_list.append(feats)
                    y_list.append([win_label, opp_archetype])
                    
    for r in train_replays: process_replay(r, X_train, y_train)
    for r in val_replays: process_replay(r, X_val, y_val)
    
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_val, y_val = np.array(X_val), np.array(y_val)
    
    os.makedirs("data", exist_ok=True)
    np.save("data/X_train.npy", X_train)
    np.save("data/y_train.npy", y_train)
    np.save("data/X_val.npy", X_val)
    np.save("data/y_val.npy", y_val)
    
    print(f"Train samples: {len(X_train)}, Val samples: {len(X_val)}")
    
if __name__ == "__main__":
    build_datasets()
