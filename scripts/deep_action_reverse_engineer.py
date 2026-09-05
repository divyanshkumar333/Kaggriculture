"""
Deep Action-by-Action Reverse Engineering for Top Kaggle Replays
"""

import sys
import json
import glob
import os
from collections import defaultdict, Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def analyze_actions_in_replay(fpath, target_player=0):
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    info = data.get("info", {})
    team_name = info.get("TeamNames", ["P0", "P1"])[target_player]
    steps = data.get("steps", [])
    
    print(f"\n{'='*80}")
    print(f"ACTION DEEP-DIVE: {team_name} in {os.path.basename(fpath)} (Reward: ${steps[-1][target_player].get('reward', 0):,.0f})")
    print(f"{'='*80}")
    
    # Track actions across days
    # Day d = turns d*24 to (d+1)*24 - 1
    day_actions = defaultdict(lambda: {
        "HIRE_count": 0,
        "BUY_LAND_count": 0,
        "BUY_ANIMAL": Counter(),
        "BUY_SEED": Counter(),
        "BUY_PRODUCT": Counter(),
        "SELL": Counter(),
        "PLANT": Counter(),
        "DIG_count": 0,
        "FEED_count": 0,
        "CARE_count": 0,
        "WATER_count": 0,
        "HARVEST_count": 0,
        "BUILD_PASTURE_count": 0,
        "BUILD_COOP_count": 0,
        "COLLECT_FERT_count": 0
    })
    
    for step_idx, step_data in enumerate(steps):
        day = step_idx // 24
        hour = step_idx % 24
        
        # Player action is in step_data[target_player]['action']
        act = step_data[target_player].get("action")
        if not act or not isinstance(act, dict):
            continue
            
        market_ops = act.get("market", [])
        farmer_op = act.get("farmer", [])
        hands_ops = act.get("hands", [])
        
        # Parse market ops
        for mop in market_ops:
            if not mop or not isinstance(mop, list): continue
            cmd = mop[0]
            if cmd == "HIRE":
                day_actions[day]["HIRE_count"] += 1
            elif cmd == "BUY_LAND":
                day_actions[day]["BUY_LAND_count"] += 1
            elif cmd == "BUY_ANIMAL" and len(mop) > 1:
                cnt = mop[2] if len(mop) > 2 else 1
                day_actions[day]["BUY_ANIMAL"][mop[1]] += cnt
            elif cmd == "BUY_SEED" and len(mop) > 1:
                cnt = mop[2] if len(mop) > 2 else 1
                day_actions[day]["BUY_SEED"][mop[1]] += cnt
            elif cmd == "BUY_PRODUCT" and len(mop) > 1:
                cnt = mop[2] if len(mop) > 2 else 1
                day_actions[day]["BUY_PRODUCT"][mop[1]] += cnt
            elif cmd == "SELL" and len(mop) > 1:
                cnt = mop[2] if len(mop) > 2 else 1
                day_actions[day]["SELL"][mop[1]] += cnt
                
        # Parse farmer and worker ops
        all_unit_ops = [farmer_op] + hands_ops
        for uop in all_unit_ops:
            if not uop or not isinstance(uop, list): continue
            cmd = uop[0]
            if cmd == "PLANT" and len(uop) > 1:
                day_actions[day]["PLANT"][uop[1]] += 1
            elif cmd == "DIG":
                day_actions[day]["DIG_count"] += 1
            elif cmd == "FEED":
                day_actions[day]["FEED_count"] += 1
            elif cmd == "CARE":
                day_actions[day]["CARE_count"] += 1
            elif cmd == "WATER":
                day_actions[day]["WATER_count"] += 1
            elif cmd == "HARVEST":
                day_actions[day]["HARVEST_count"] += 1
            elif cmd == "BUILD_PASTURE":
                day_actions[day]["BUILD_PASTURE_count"] += 1
            elif cmd == "BUILD_COOP":
                day_actions[day]["BUILD_COOP_count"] += 1
            elif cmd == "COLLECT_FERTILIZER":
                day_actions[day]["COLLECT_FERT_count"] += 1

    # Print Day-by-Day Strategic Action Profile
    print(f"{'Day':4s} | {'HIRE':4s} | {'LAND':4s} | {'Animals Bought':20s} | {'Seeds Bought':24s} | {'Plants Planted':22s} | {'Digs':4s} | {'Sales Profile'}")
    print("-" * 120)
    for d in range(30):
        da = day_actions[d]
        hires = str(da["HIRE_count"]) if da["HIRE_count"] > 0 else "-"
        land = str(da["BUY_LAND_count"]) if da["BUY_LAND_count"] > 0 else "-"
        anim = ", ".join([f"{k}:{v}" for k, v in da["BUY_ANIMAL"].items()]) or "-"
        seeds = ", ".join([f"{k}:{v}" for k, v in da["BUY_SEED"].items()]) or "-"
        plants = ", ".join([f"{k}:{v}" for k, v in da["PLANT"].items()]) or "-"
        digs = str(da["DIG_count"]) if da["DIG_count"] > 0 else "-"
        sales = ", ".join([f"{k}:{v}" for k, v in da["SELL"].items()]) or "-"
        
        print(f"D{d:2d}  | {hires:>4s} | {land:>4s} | {anim:20s} | {seeds:24s} | {plants:22s} | {digs:>4s} | {sales}")

if __name__ == "__main__":
    replays = [
        ("episode-103388734-replay.json", 0), # AI After Hours ($162.8k)
        ("kaggle_episodes/episode-104882243-replay.json", 0), # yjshyfy ($116.5k)
        ("episode-103979994-replay.json", 0), # Thayaparan ($114.8k)
        ("kaggle_episodes/episode-105590375-replay.json", 0), # Aditya Bharadwaj ($97.2k)
    ]
    for rpath, pidx in replays:
        if os.path.exists(rpath):
            analyze_actions_in_replay(rpath, pidx)
