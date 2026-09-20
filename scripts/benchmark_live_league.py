"""
Phase 7.5: Benchmark V057 against actual replay-derived agents from CURRENT_LIVE_STYLE_LEAGUE
"""

import os
import sys
import json
import csv
import glob
from collections import defaultdict
from pathlib import Path
import concurrent.futures

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_clusters():
    traces = glob.glob(str(ROOT / "RESEARCH" / "opponents" / "live_league" / "traces" / "*.json"))
    clusters = defaultdict(list)
    
    for t in traces:
        name = os.path.basename(t)
        if "Divyansh" in name or "divyansh" in name.lower():
            continue
        with open(t, encoding='utf-8', errors='ignore') as f:
            trace = json.load(f)
            
        hire_count = 0
        for step in range(min(24, len(trace))):
            action = trace[step]
            if "market" in action:
                hire_count += sum(1 for m in action["market"] if m and m[0] == "HIRE")
                
        first_plant = "NONE"
        for step in range(len(trace)):
            farmer_a = trace[step].get("farmer", [])
            if farmer_a and farmer_a[0] == "PLANT":
                first_plant = farmer_a[1] if len(farmer_a) > 1 else "NONE"
                break
                
        first_animal = "NONE"
        for step in range(len(trace)):
            farmer_a = trace[step].get("farmer", [])
            if farmer_a and farmer_a[0] in ("BUILD_COOP", "BUILD_PASTURE"):
                first_animal = farmer_a[0]
                break
                
        cluster_name = f"D0-HIRES:{hire_count}_PLANT:{first_plant}_STRUC:{first_animal}"
        clusters[cluster_name].append(t)
    return clusters

def _worker(args):
    agent_a_path, trace_path, seed, seat_a = args
    import importlib.util
    from kaggle_environments import make
    
    # Load V057
    spec_a = importlib.util.spec_from_file_location("_agent", agent_a_path)
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    agent_a = mod_a.agent
    
    # Load Replay Agent
    replay_agent_path = os.path.join(ROOT, "agents", "replay_agent.py")
    spec_r = importlib.util.spec_from_file_location("_replay", replay_agent_path)
    mod_r = importlib.util.module_from_spec(spec_r)
    spec_r.loader.exec_module(mod_r)
    agent_r = mod_r.agent
    
    env = make("kaggriculture", configuration={"episodeSteps": 721, "randomSeed": seed}, debug=False)
    
    # We must patch os.environ in the worker
    os.environ["REPLAY_AGENT_TRACE"] = trace_path
    
    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (farm.get("hands") or [])], "market": []}
            
    if seat_a == 0:
        env.run([lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg), lambda obs, cfg, _r=agent_r: _safe(_r, obs, cfg)])
    else:
        env.run([lambda obs, cfg, _r=agent_r: _safe(_r, obs, cfg), lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg)])
        
    final = env.steps[-1]
    r_a = float((final[0] if seat_a == 0 else final[1]).reward or 0)
    r_r = float((final[1] if seat_a == 0 else final[0]).reward or 0)
    
    score = 1.0 if r_a > r_r else 0.5 if r_a == r_r else 0.0
    return (seed, seat_a, r_a, r_r, score)

def main():
    agent_a_path = os.path.join(ROOT, "agents", "v057_deep_frontrun.py")
    clusters = load_clusters()
    
    # Select top 5 clusters, 1 representative trace per cluster
    representatives = []
    for c, files in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        representatives.append((c, files[0]))
        
    seeds = list(range(9000, 9008)) # 8 custom seeds
    tasks = []
    
    for c, trace_path in representatives:
        for s in seeds:
            tasks.append((agent_a_path, trace_path, s, 0))
            tasks.append((agent_a_path, trace_path, s, 1))
            
    print(f"Benchmarking V057 against {len(representatives)} live replay styles ({len(tasks)} games)")
    
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    csv_path = os.path.join(ROOT, "reports", "EXP038_LIVE_LEAGUE_BENCHMARK_raw.csv")
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Cluster", "Trace", "Seed", "V057_Seat", "V057_Cash", "Opponent_Cash", "V057_Score"])
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            future_to_trace = {executor.submit(_worker, t): (t[1], [rep[0] for rep in representatives if rep[1] == t[1]][0]) for t in tasks}
            for future in concurrent.futures.as_completed(future_to_trace):
                trace_path, cluster = future_to_trace[future]
                seed, seat_a, r_a, r_r, score = future.result()
                trace_name = os.path.basename(trace_path)
                writer.writerow([cluster, trace_name, seed, seat_a, r_a, r_r, score])
                f.flush()
                
    print(f"Saved {csv_path}")

if __name__ == "__main__":
    main()
