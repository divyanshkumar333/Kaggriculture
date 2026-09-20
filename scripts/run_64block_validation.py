"""
Phase 7.5: 64-block real-artifact validation
Runs V057 vs Kaito and V057 vs Barnyard (both seats, 32 discovery blocks + 64 validation blocks).
Saves raw per-game results.
"""

import argparse
import csv
import os
import sys
from pathlib import Path
import importlib.util
import concurrent.futures

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_game(agent_a_path, agent_b_path, seed, seat_a, max_steps=720):
    from kaggle_environments import make
    agent_a = load_agent(agent_a_path)
    agent_b = load_agent(agent_b_path)
    
    env = make("kaggriculture", configuration={"episodeSteps": max_steps + 1, "randomSeed": seed}, debug=False)
    
    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception as e:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (farm.get("hands") or [])], "market": []}

    if seat_a == 0:
        agents = [lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg), lambda obs, cfg, _b=agent_b: _safe(_b, obs, cfg)]
    else:
        agents = [lambda obs, cfg, _b=agent_b: _safe(_b, obs, cfg), lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg)]
        
    env.run(agents)
    
    final = env.steps[-1]
    
    if seat_a == 0:
        r_a = final[0].reward or 0
        r_b = final[1].reward or 0
    else:
        r_a = final[1].reward or 0
        r_b = final[0].reward or 0
        
    return float(r_a), float(r_b)

def worker(args):
    agent_a_path, agent_b_path, seed = args
    r0_a, r0_b = run_game(agent_a_path, agent_b_path, seed, seat_a=0)
    r1_a, r1_b = run_game(agent_a_path, agent_b_path, seed, seat_a=1)
    
    score0 = 1 if r0_a > r0_b else 0.5 if r0_a == r0_b else 0
    score1 = 1 if r1_a > r1_b else 0.5 if r1_a == r1_b else 0
    
    return [
        (seed, 0, r0_a, r0_b, score0),
        (seed, 1, r1_a, r1_b, score1)
    ]

def main():
    agent_a_path = os.path.join(ROOT, "agents", "v057_deep_frontrun.py")
    
    opponents = [
        ("Kaito", os.path.join(ROOT, "RESEARCH", "external", "kaito_v27_real", "main.py")),
        ("Barnyard", os.path.join(ROOT, "RESEARCH", "external", "barnyard_real", "main.py"))
    ]
    
    # 32 discovery blocks (10000..10031)
    # 64 validation blocks (11000..11063)
    discovery_seeds = list(range(10000, 10032))
    validation_seeds = list(range(11000, 11064))
    seeds = discovery_seeds + validation_seeds
    
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    
    for opp_name, opp_path in opponents:
        print(f"Benchmarking V057 vs {opp_name}...")
        tasks = [(agent_a_path, opp_path, s) for s in seeds]
        
        csv_path = os.path.join(ROOT, "reports", f"EXP038_BASE_V057_vs_{opp_name}_raw.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Seed", "V057_Seat", "V057_Cash", "Opponent_Cash", "V057_Score"])
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                for res in executor.map(worker, tasks):
                    for row in res:
                        writer.writerow(row)
                    f.flush()
                        
        print(f"Saved {csv_path}")

if __name__ == "__main__":
    main()
