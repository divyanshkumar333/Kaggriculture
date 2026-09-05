"""
Detailed Milestone Comparison: Episode 103388734 ($162.8K Replay) vs V025-A
===========================================================================
Extracts full inventory, crops, livestock, labor, and bank at all 13 checkpoints.
"""

import os
import json
import importlib.util
import pandas as pd
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def extract_stats(farm):
    cows, sheep, straw, wheat, melons, carrots = 0, 0, 0, 0, 0, 0
    for r in farm["tiles"]:
        for t in r:
            if isinstance(t, dict):
                k = t.get("kind")
                if k in ["PASTURE", "COOP"]:
                    an = t.get("animal")
                    if an == "COW": cows += 1
                    elif an == "SHEEP": sheep += 1
                elif k == "PLANT":
                    cr = t.get("crop")
                    if cr == "STRAWBERRY": straw += 1
                    elif cr == "WHEAT": wheat += 1
                    elif cr == "MELON": melons += 1
                    elif cr == "CARROT": carrots += 1
    return {
        "money": int(round(farm["money"])),
        "cows": cows,
        "sheep": sheep,
        "straw": straw,
        "wheat": wheat,
        "melons": melons,
        "workers": 1 + len(farm["hands"]),
        "quadrants": len(farm["unlocked_quadrants"]),
    }

def main():
    with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
        top_data = json.load(f)
    top_steps = top_data["steps"]
    
    agent_func = load_agent("agents/v025_a_aggressive_cows.py")
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
    env.run([agent_func, "random"])
    v25_steps = env.steps
    
    checkpoints = [0, 3, 5, 6, 8, 10, 12, 15, 18, 21, 24, 27, 29]
    
    rows = []
    for d in checkpoints:
        top_s = min(d * 24 + 23, len(top_steps) - 1)
        v25_s = min(d * 24 + 23, len(v25_steps) - 1)
        
        top_obs = top_steps[top_s][1]["observation"]["farms"][1]
        v25_obs = v25_steps[v25_s][0]["observation"]["farms"][0]
        
        t = extract_stats(top_obs)
        v = extract_stats(v25_obs)
        
        rows.append({
            "DAY": f"D{d}",
            "TOP_BANK": f"${t['money']:,}",
            "V25_BANK": f"${v['money']:,}",
            "TOP_COWS": t["cows"],
            "V25_COWS": v["cows"],
            "TOP_STRAW": t["straw"],
            "V25_STRAW": v["straw"],
            "TOP_WHEAT": t["wheat"],
            "V25_WHEAT": v["wheat"],
            "TOP_SHEEP": t["sheep"],
            "V25_SHEEP": v["sheep"],
            "TOP_WORKERS": t["workers"],
            "V25_WORKERS": v["workers"],
            "TOP_QUADS": t["quadrants"],
            "V25_QUADS": v["quadrants"],
        })
        
    df = pd.DataFrame(rows)
    print("=" * 135)
    print("13-MILESTONE DIRECT REPLAY COMPARISON: TOP REPLAY ($162.8K) VS V025-A (Seed 42)")
    print("=" * 135)
    print(df.to_string(index=False))
    
    os.makedirs("scratch", exist_ok=True)
    df.to_csv("scratch/v025_replay_milestones.csv", index=False)

if __name__ == "__main__":
    main()
