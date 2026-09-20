"""
Phase 7.5: Divergence Analysis
Runs V057 vs Kaito on a few seeds and extracts state snapshots at days 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 29.
Calculates cash difference immediately before and after major market events.
"""

import os
import sys
import csv
from pathlib import Path
import importlib.util

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def analyze_match(agent_a_path, agent_b_path, seed, name_a="V057", name_b="Opponent"):
    from kaggle_environments import make
    agent_a = load_agent(agent_a_path)
    agent_b = load_agent(agent_b_path)
    
    env = make("kaggriculture", configuration={"episodeSteps": 721, "randomSeed": seed}, debug=False)
    
    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (farm.get("hands") or [])], "market": []}

    # Always seat 0 for V057
    env.run([lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg), lambda obs, cfg, _b=agent_b: _safe(_b, obs, cfg)])
    
    snapshots = []
    market_events = []
    
    target_days = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 29]
    
    for step_num, step_data in enumerate(env.steps):
        obs = step_data[0]["observation"]
        day = obs.get("day", step_num // 24)
        hour = obs.get("step", step_num) % 24
        
        r_a = step_data[0].reward or 0
        r_b = step_data[1].reward or 0
        
        # Take snapshot at hour 0 of target days
        if day in target_days and hour == 0:
            farm_a = obs["farms"][0]
            farm_b = obs["farms"][1]
            
            plants_a = sum(1 for row in farm_a["tiles"] for cell in row if isinstance(cell, dict) and cell.get("kind") == "PLANT")
            plants_b = sum(1 for row in farm_b["tiles"] for cell in row if isinstance(cell, dict) and cell.get("kind") == "PLANT")
            
            snapshots.append({
                "Seed": seed,
                "Day": day,
                "V057_Cash": r_a,
                "Opp_Cash": r_b,
                "Cash_Diff": r_a - r_b,
                "V057_Plants": plants_a,
                "Opp_Plants": plants_b
            })
            
        # Analyze market events (if any agent sold a lot)
        if step_num > 0:
            prev_r_a = env.steps[step_num - 1][0].reward or 0
            prev_r_b = env.steps[step_num - 1][1].reward or 0
            
            a_delta = r_a - prev_r_a
            b_delta = r_b - prev_r_b
            
            if a_delta > 500 or b_delta > 500:
                market_events.append({
                    "Seed": seed,
                    "Step": step_num,
                    "Day": day,
                    "Hour": hour,
                    "Prev_Diff": prev_r_a - prev_r_b,
                    "Post_Diff": r_a - r_b,
                    "V057_Sale": a_delta,
                    "Opp_Sale": b_delta
                })
                
    return snapshots, market_events

def main():
    agent_a_path = os.path.join(ROOT, "agents", "v057_deep_frontrun.py")
    kaito_path = os.path.join(ROOT, "RESEARCH", "external", "kaito_v27_real", "main.py")
    
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    
    all_snapshots = []
    all_market_events = []
    
    seeds = [10000, 10001, 10002, 10003, 10004]
    print(f"Analyzing {len(seeds)} seeds for Divergence Analysis...")
    for seed in seeds:
        snaps, events = analyze_match(agent_a_path, kaito_path, seed, "V057", "Kaito")
        all_snapshots.extend(snaps)
        all_market_events.extend(events)
        
    with open(os.path.join(ROOT, "reports", "v057_snapshots.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Seed", "Day", "V057_Cash", "Opp_Cash", "Cash_Diff", "V057_Plants", "Opp_Plants"])
        writer.writeheader()
        for row in all_snapshots:
            writer.writerow(row)
            
    with open(os.path.join(ROOT, "reports", "v057_market_events.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Seed", "Step", "Day", "Hour", "Prev_Diff", "Post_Diff", "V057_Sale", "Opp_Sale"])
        writer.writeheader()
        for row in all_market_events:
            writer.writerow(row)
            
    print("Saved reports/v057_snapshots.csv and reports/v057_market_events.csv")

if __name__ == "__main__":
    main()
