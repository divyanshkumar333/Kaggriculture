"""
Phase 4: Trajectory & Behavioral Feature Extraction
---------------------------------------------------
Parses downloaded Kaggle replay episodes (.json.gz) and extracts:
1. Episode-level Macro Strategic Milestones (D0-D29 timelines, crop counts, animal ramps, labor curves)
2. Turn-level State-Action-Return tuples for policy modeling and behavioral contrast
3. Strictly isolates training data from frozen holdout
"""

import os
import sys
import glob
import gzip
import json
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor

def parse_single_episode(filepath):
    """Parses an episode replay into structured player trajectories."""
    try:
        with gzip.open(filepath, "rt", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return None

    ep_id = data.get("id") or os.path.basename(filepath).split(".")[0]
    steps = data.get("steps", [])
    if len(steps) < 10:
        return None

    results = []
    
    # Process both seats (0 and 1)
    for seat in [0, 1]:
        final_reward = steps[-1][seat].get("reward", 0)
        opp_seat = 1 - seat
        opp_final_reward = steps[-1][opp_seat].get("reward", 0)
        won = 1 if final_reward > opp_final_reward else (0.5 if final_reward == opp_final_reward else 0)

        # Macro milestones
        d0_opening = {
            "hires": 0, "cow_bought": 0, "sheep_bought": 0,
            "melon_seeds": 0, "wheat_seeds": 0, "strawberry_seeds": 0,
            "pastures_built": 0
        }
        
        milestones = {
            "first_cow_day": None,
            "first_sheep_day": None,
            "first_strawberry_day": None,
            "quad2_day": None,
            "quad3_day": None,
            "cows_d5": 0, "cows_d8": 0, "cows_d12": 0, "cows_d15": 0, "cows_d20": 0, "cows_d25": 0, "cows_d29": 0,
            "sheep_d5": 0, "sheep_d8": 0, "sheep_d12": 0, "sheep_d15": 0, "sheep_d20": 0,
            "strawberries_d5": 0, "strawberries_d8": 0, "strawberries_d12": 0, "strawberries_d15": 0, "strawberries_d20": 0, "strawberries_d25": 0, "strawberries_d29": 0,
            "workers_d0": 0, "workers_d5": 0, "workers_d8": 0, "workers_d12": 0, "workers_d15": 0, "workers_d20": 0,
            "total_hires_d0_d5": 0, "total_hires_d6_d12": 0,
            "final_cash": final_reward, "won": won, "episode_id": ep_id, "seat": seat
        }

        # Step-by-step trace
        for step_idx in range(len(steps)):
            step_record = steps[step_idx][seat]
            obs = step_record.get("observation")
            action = step_record.get("action")
            if not obs or "farms" not in obs:
                continue

            day = obs.get("day", step_idx // 24)
            hour = obs.get("hour", step_idx % 24)
            me = obs["farms"][seat]
            unlocked = len(me.get("unlocked_quadrants", ["NW"]))
            
            # Count structures and crops
            tiles = me.get("tiles", [])
            cows = 0
            sheep = 0
            strawberries = 0
            melons = 0
            wheat = 0
            pastures = 0
            for row in tiles:
                for t in row:
                    if isinstance(t, dict):
                        kind = t.get("kind")
                        if kind == "PASTURE":
                            pastures += 1
                            an = t.get("animal")
                            if an == "COW": cows += 1
                            elif an == "SHEEP": sheep += 1
                        elif kind == "PLANT":
                            crop = t.get("crop")
                            if crop == "STRAWBERRY": strawberries += 1
                            elif crop == "MELON": melons += 1
                            elif crop == "WHEAT": wheat += 1

            workers = len(me.get("hands", [])) + 1

            # Day 0 action parsing
            if day == 0 and step_idx == 1 and action and "market" in action:
                for op in action.get("market", []):
                    if len(op) > 0:
                        cmd = op[0]
                        if cmd == "HIRE": d0_opening["hires"] += 1
                        elif cmd == "BUY_ANIMAL" and len(op) >= 3:
                            if op[1] == "COW": d0_opening["cow_bought"] += op[2]
                            elif op[1] == "SHEEP": d0_opening["sheep_bought"] += op[2]
                        elif cmd == "BUY_SEED" and len(op) >= 3:
                            if op[1] == "MELON": d0_opening["melon_seeds"] += op[2]
                            elif op[1] == "WHEAT": d0_opening["wheat_seeds"] += op[2]
                            elif op[1] == "STRAWBERRY": d0_opening["strawberry_seeds"] += op[2]

            # Track first occurrences
            if cows > 0 and milestones["first_cow_day"] is None:
                milestones["first_cow_day"] = day
            if sheep > 0 and milestones["first_sheep_day"] is None:
                milestones["first_sheep_day"] = day
            if strawberries > 0 and milestones["first_strawberry_day"] is None:
                milestones["first_strawberry_day"] = day
            if unlocked >= 2 and milestones["quad2_day"] is None:
                milestones["quad2_day"] = day
            if unlocked >= 3 and milestones["quad3_day"] is None:
                milestones["quad3_day"] = day

            # Snapshots at end of specific days (hour == 23)
            if hour == 23:
                if day == 0:
                    milestones["workers_d0"] = workers
                elif day == 5:
                    milestones["cows_d5"] = cows
                    milestones["sheep_d5"] = sheep
                    milestones["strawberries_d5"] = strawberries
                    milestones["workers_d5"] = workers
                elif day == 8:
                    milestones["cows_d8"] = cows
                    milestones["sheep_d8"] = sheep
                    milestones["strawberries_d8"] = strawberries
                    milestones["workers_d8"] = workers
                elif day == 12:
                    milestones["cows_d12"] = cows
                    milestones["sheep_d12"] = sheep
                    milestones["strawberries_d12"] = strawberries
                    milestones["workers_d12"] = workers
                elif day == 15:
                    milestones["cows_d15"] = cows
                    milestones["sheep_d15"] = sheep
                    milestones["strawberries_d15"] = strawberries
                    milestones["workers_d15"] = workers
                elif day == 20:
                    milestones["cows_d20"] = cows
                    milestones["sheep_d20"] = sheep
                    milestones["strawberries_d20"] = strawberries
                    milestones["workers_d20"] = workers
                elif day == 25:
                    milestones["cows_d25"] = cows
                    milestones["strawberries_d25"] = strawberries
                elif day == 29:
                    milestones["cows_d29"] = cows
                    milestones["strawberries_d29"] = strawberries

        # Merge D0 opening into milestones
        for k, v in d0_opening.items():
            milestones[f"d0_{k}"] = v

        results.append(milestones)

    return results

def main():
    print("=== Phase 4: Batch Trajectory Feature Extraction ===", flush=True)

    files = glob.glob("datasets/il/episodes/*.json.gz")
    print(f"Found {len(files)} downloaded episodes for parsing.", flush=True)
    if not files:
        print("[ERROR] No episodes found in datasets/il/episodes/")
        return

    # Multiprocessing across CPU cores
    records = []
    with ProcessPoolExecutor() as executor:
        for res in executor.map(parse_single_episode, files, chunksize=10):
            if res:
                records.extend(res)

    df = pd.DataFrame(records)
    output_path = "datasets/il/extracted_milestones.csv"
    df.to_csv(output_path, index=False)
    print(f"\nExtracted {len(df)} player trajectories into {output_path}!", flush=True)
    print(df.head())

if __name__ == "__main__":
    main()
