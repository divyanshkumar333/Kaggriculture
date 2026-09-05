import gzip
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def analyze_top_replay(ep_id, p0_name, p1_name):
    path = f"datasets/il/episodes/{ep_id}.json.gz"
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return
    
    with gzip.open(path, "rt", encoding="utf-8") as f:
        ep = json.load(f)
        
    steps = ep["steps"]
    print(f"=== REPLAY {ep_id}: {p0_name} vs {p1_name} ===")
    print(f"Total steps: {len(steps)}")
    
    header = f"{'Day':4s} | {'P0 Cash':10s} {'Cows':4s} {'Shp':4s} {'Strw':4s} {'Mln':4s} {'Wht':4s} {'Wrk':4s} {'Qd':2s} | {'P1 Cash':10s} {'Cows':4s} {'Shp':4s} {'Strw':4s} {'Mln':4s} {'Wht':4s} {'Wrk':4s} {'Qd':2s}"
    print(header)
    print("-" * len(header))
    
    for day in range(0, 30, 2):
        step_idx = min(day * 24 + 1, len(steps) - 1)
        obs = steps[step_idx][0]["observation"]
        
        row_parts = [f"D{day:2d} "]
        for p in [0, 1]:
            farm = obs["farms"][p]
            money = farm["money"]
            tiles = farm["tiles"]
            cows = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("animal") == "COW")
            sheep = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("animal") == "SHEEP")
            straw = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("crop") == "STRAWBERRY")
            melons = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("crop") == "MELON")
            wheat = sum(1 for r in tiles for t in r if isinstance(t, dict) and t.get("crop") == "WHEAT")
            workers = 1 + len(farm.get("hands", []))
            quads = len(farm.get("unlocked_quadrants", []))
            row_parts.append(f"{money:10,.0f} {cows:4d} {sheep:4d} {straw:4d} {melons:4d} {wheat:4d} {workers:4d} {quads:2d}")
        print(" | ".join(row_parts))
        
    final_step = steps[-1]
    print(f"Final Score: P0 ({p0_name}) = {final_step[0]['reward']:,.0f} | P1 ({p1_name}) = {final_step[1]['reward']:,.0f}")
    print()

if __name__ == "__main__":
    analyze_top_replay("93221407", "Thomas Tschinkel", "カワシギ")
