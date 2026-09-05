"""
Current Meta Diff: Compare candidate telemetry against top Kaggle replay trajectories
"""

import sys
import json
import importlib.util
import numpy as np
from kaggle_environments import make

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def run_telemetry(agent_path, seed=42):
    spec = importlib.util.spec_from_file_location("cand_mod", agent_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod.agent, "random"])
    
    steps = env.steps
    days_to_check = [0, 2, 4, 5, 6, 7, 8, 10, 12, 15, 18, 21, 24, 27, 29]
    telemetry = {}
    
    for d in days_to_check:
        step_idx = min(d * 24, len(steps) - 1)
        farm = steps[step_idx][0]["observation"]["farms"][0]
        tiles = farm.get("tiles", [])
        cows = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PASTURE" and t.get("animal") == "COW")
        sheep = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PASTURE" and t.get("animal") == "SHEEP")
        strawberries = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY")
        wheat = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT")
        melons = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON")
        quadrants = len(farm.get("unlocked_quadrants", []))
        workers = len(farm.get("hands", [])) + 1
        money = farm.get("money", 0)
        
        telemetry[d] = {
            "money": money,
            "cows": cows,
            "sheep": sheep,
            "strawberries": strawberries,
            "wheat": wheat,
            "melons": melons,
            "quadrants": quadrants,
            "workers": workers
        }
    return float(steps[-1][0]["reward"]), telemetry

if __name__ == "__main__":
    agent = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    r, tel = run_telemetry(agent, seed=42)
    print(f"\nTelemetry for {agent} (Seed 42, Final Reward: ${r:,.0f}):")
    print(f"{'Day':4s} | {'Bank':>10s} | {'Cows':>5s} | {'Sheep':>5s} | {'Strawb':>7s} | {'Wheat':>6s} | {'Melons':>7s} | {'Quads':>6s} | {'Workers':>8s}")
    print("-" * 75)
    for d, t in tel.items():
        print(f"D{d:2d}  | ${t['money']:>9,.0f} | {t['cows']:>5d} | {t['sheep']:>5d} | {t['strawberries']:>7d} | {t['wheat']:>6d} | {t['melons']:>7d} | {t['quadrants']:>6d} | {t['workers']:>8d}")
