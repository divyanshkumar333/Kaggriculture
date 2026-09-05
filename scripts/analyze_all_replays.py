"""
Comprehensive Replay Analyzer: Parse all downloaded Kaggle replays to extract top meta strategies
"""

import sys
import json
import glob
import os
import numpy as np

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def analyze_all_replays():
    files = glob.glob("kaggle_episodes/episode-*-replay.json") + glob.glob("episode-*-replay.json")
    files = list(set(files))
    print(f"Total replay files found: {len(files)}")
    
    matches = []
    
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            continue
            
        info = data.get("info", {})
        team_names = info.get("TeamNames", ["Player0", "Player1"])
        ep_id = info.get("EpisodeId", os.path.basename(fpath))
        steps = data.get("steps", [])
        if len(steps) < 700:
            continue
            
        r0 = float(steps[-1][0].get("reward", 0))
        r1 = float(steps[-1][1].get("reward", 0))
        
        days_to_check = [0, 2, 4, 5, 6, 7, 8, 10, 12, 15, 18, 21, 24, 27, 29]
        
        match_record = {
            "file": fpath,
            "episode_id": ep_id,
            "team_0": str(team_names[0]) if len(team_names) > 0 else "Unknown",
            "team_1": str(team_names[1]) if len(team_names) > 1 else "Unknown",
            "reward_0": r0,
            "reward_1": r1,
            "winner": 0 if r0 > r1 else (1 if r1 > r0 else -1),
            "top_score": max(r0, r1),
            "p0_trajectory": {},
            "p1_trajectory": {}
        }
        
        for d in days_to_check:
            step_idx = min(d * 24, len(steps) - 1)
            obs = steps[step_idx][0].get("observation", {})
            farms = obs.get("farms", [])
            for p in [0, 1]:
                if len(farms) > p:
                    farm = farms[p]
                    tiles = farm.get("tiles", [])
                    cows = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PASTURE" and t.get("animal") == "COW")
                    sheep = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PASTURE" and t.get("animal") == "SHEEP")
                    strawberries = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY")
                    wheat = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT")
                    melons = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON")
                    quadrants = len(farm.get("unlocked_quadrants", []))
                    workers = len(farm.get("hands", [])) + 1
                    money = farm.get("money", 0)
                    
                    traj_dict = match_record[f"p{p}_trajectory"]
                    traj_dict[d] = {
                        "money": money,
                        "cows": cows,
                        "sheep": sheep,
                        "strawberries": strawberries,
                        "wheat": wheat,
                        "melons": melons,
                        "quadrants": quadrants,
                        "workers": workers
                    }
                    
        matches.append(match_record)
        
    print(f"Successfully processed {len(matches)} valid 720-step matches")
    
    matches.sort(key=lambda m: m["top_score"], reverse=True)
    
    print("\n" + "="*80)
    print("TOP 15 HIGHEST SCORING REPLAY PERFORMANCES ACROSS ALL PUBLIC EPISODES")
    print("="*80)
    for idx, m in enumerate(matches[:15], 1):
        winner_p = m["winner"]
        win_team = m[f"team_{winner_p}"] if winner_p in [0, 1] else "Tie"
        win_score = m["top_score"]
        loser_p = 1 - winner_p if winner_p in [0, 1] else 0
        loser_team = m[f"team_{loser_p}"]
        loser_score = m[f"reward_{loser_p}"]
        print(f"#{idx:2d} Ep {str(m['episode_id']):12s}: Winner: {win_team[:20]:20s} ${win_score:,.0f} vs {loser_team[:20]:20s} ${loser_score:,.0f}")

    # Inspect top 3 unique non-Divyansh winning trajectories in detail
    top_external_matches = [m for m in matches if m["winner"] != -1 and "Divyansh" not in m[f"team_{m['winner']}"]]
    
    print("\n" + "="*80)
    print("DETAILED DAY-BY-DAY TELEMETRY FOR TOP 3 EXTERNAL WINNING AGENTS")
    print("="*80)
    
    for i, m in enumerate(top_external_matches[:3], 1):
        win_p = m["winner"]
        team = m[f"team_{win_p}"]
        score = m["top_score"]
        ep = m["episode_id"]
        traj = m[f"p{win_p}_trajectory"]
        print(f"\n--- Rank #{i}: {team} (Ep {ep}, Final Score: ${score:,.0f}) ---")
        print(f"{'Day':4s} | {'Bank':>10s} | {'Cows':>5s} | {'Strawb':>7s} | {'Wheat':>6s} | {'Melons':>7s} | {'Quads':>6s} | {'Workers':>8s}")
        print("-" * 65)
        for d in days_to_check:
            if d in traj:
                t = traj[d]
                print(f"D{d:2d}  | ${t['money']:>9,.0f} | {t['cows']:>5d} | {t['strawberries']:>7d} | {t['wheat']:>6d} | {t['melons']:>7d} | {t['quadrants']:>6d} | {t['workers']:>8d}")

    # Inspect Divyansh Kumar's winning match in Ep 105710071 (V025-A in action)
    v25_match = next((m for m in matches if str(m["episode_id"]) == "105710071"), None)
    if v25_match:
        print(f"\n--- V025-A Live Match Telemetry (Ep 105710071, Divyansh Kumar, Score: ${v25_match['reward_1']:,.0f}) ---")
        traj_v25 = v25_match["p1_trajectory"]
        print(f"{'Day':4s} | {'Bank':>10s} | {'Cows':>5s} | {'Strawb':>7s} | {'Wheat':>6s} | {'Melons':>7s} | {'Quads':>6s} | {'Workers':>8s}")
        print("-" * 65)
        for d in days_to_check:
            if d in traj_v25:
                t = traj_v25[d]
                print(f"D{d:2d}  | ${t['money']:>9,.0f} | {t['cows']:>5d} | {t['strawberries']:>7d} | {t['wheat']:>6d} | {t['melons']:>7d} | {t['quadrants']:>6d} | {t['workers']:>8d}")
                
    return matches

if __name__ == "__main__":
    analyze_all_replays()
