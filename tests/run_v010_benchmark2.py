import os
import sys
import json
import glob
import subprocess
import numpy as np
from collections import defaultdict

AGENTS = ["agents/v010_a_control.py", "agents/v010_b_land_expansion.py"]
OPPONENTS = ["random", "starter", "agents/melon_maxxer.py"]
GAMES_PER_OPPONENT = 30
START_SEED = 2000

def run_experiment(agent, opponent, start_seed, games):
    print(f"Running {games} games: {agent} vs {opponent}")
    cmd = [
        ".venv\\Scripts\\python.exe", "experiments.py",
        "--agent", agent,
        "--opponent", opponent,
        "--games", str(games),
        "--seed_start", str(start_seed)
    ]
    subprocess.run(cmd, capture_output=True, text=True)

def collect_metrics(start_seed, games):
    metrics_list = []
    for i in range(games):
        seed = start_seed + i
        f0 = f"experiments/metrics/game_{seed}_p0.json"
        f1 = f"experiments/metrics/game_{seed}_p1.json"
        
        # Determine which file contains the agent metrics
        data = None
        if os.path.exists(f0):
            with open(f0) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass
        elif os.path.exists(f1):
            with open(f1) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        if data:
            metrics_list.append(data)
            
    # Clean up metrics files so they don't interfere with next run
    for i in range(games):
        seed = start_seed + i
        for f in [f"experiments/metrics/game_{seed}_p0.json", f"experiments/metrics/game_{seed}_p1.json"]:
            if os.path.exists(f):
                os.remove(f)
                
    return metrics_list

def calculate_stats(metrics_list):
    if not metrics_list:
        return {}
        
    stats = {}
    stats["final_money"] = [m["economy"].get("final_money", 0) for m in metrics_list]
    stats["total_revenue"] = [m["economy"].get("total_revenue", 0) for m in metrics_list]
    stats["seed_spending"] = [m["economy"].get("seed_spending", 0) for m in metrics_list]
    stats["worker_spending"] = [m["economy"].get("worker_spending", 0) for m in metrics_list]
    stats["land_spending"] = [m["economy"].get("land_spending", 0) for m in metrics_list]
    
    # Labor metrics
    stats["hired"] = [m["workers"].get("hired", 0) for m in metrics_list]
    stats["useful_actions"] = [m["workers"].get("useful_actions", 0) + m["farmer"].get("useful_actions", 0) for m in metrics_list]
    stats["movement_actions"] = [m["workers"].get("movement_actions", 0) + m["farmer"].get("movement_actions", 0) for m in metrics_list]
    stats["idle_turns"] = [m["workers"].get("idle_turns", 0) for m in metrics_list]
    stats["water_misses"] = [m["water"].get("misses", 0) for m in metrics_list]
    
    stats["crop_deaths"] = []
    for m in metrics_list:
        deaths = sum(c.get("deaths", 0) for c in m["crops"].values())
        stats["crop_deaths"].append(deaths)
        
    # Calculate means
    means = {k: np.mean(v) for k, v in stats.items()}
    medians = {k: np.median(v) for k, v in stats.items()}
    stds = {k: np.std(v) for k, v in stats.items()}
    
    means["movement_efficiency"] = means["useful_actions"] / (means["useful_actions"] + means["movement_actions"]) if means["useful_actions"] + means["movement_actions"] > 0 else 0
    
    return {
        "raw": stats,
        "mean": means,
        "median": medians,
        "std": stds,
        "min": {k: np.min(v) for k, v in stats.items()},
        "max": {k: np.max(v) for k, v in stats.items()},
        "count": len(metrics_list)
    }

def main():
    results = defaultdict(lambda: defaultdict(dict))
    
    agent_raw_lists = defaultdict(lambda: defaultdict(list))
    total_games = defaultdict(int)
    
    for agent in AGENTS:
        for opponent in OPPONENTS:
            run_experiment(agent, opponent, START_SEED, GAMES_PER_OPPONENT)
            metrics = collect_metrics(START_SEED, GAMES_PER_OPPONENT)
            
            stats = calculate_stats(metrics)
            results[agent][opponent] = stats
            
            if stats:
                for k, v in stats["raw"].items():
                    agent_raw_lists[agent][k].extend(v)
            total_games[agent] += len(metrics)
            
    # Consolidate overall metrics per agent
    for agent in AGENTS:
        if agent_raw_lists[agent]:
            raw = agent_raw_lists[agent]
            means = {k: np.mean(v) for k, v in raw.items()}
            medians = {k: np.median(v) for k, v in raw.items()}
            stds = {k: np.std(v) for k, v in raw.items()}
            means["movement_efficiency"] = means["useful_actions"] / (means["useful_actions"] + means["movement_actions"]) if means["useful_actions"] + means["movement_actions"] > 0 else 0
            
            overall = {
                "raw": dict(raw),
                "mean": means,
                "median": medians,
                "std": stds,
                "min": {k: np.min(v) for k, v in raw.items()},
                "max": {k: np.max(v) for k, v in raw.items()},
                "count": total_games[agent]
            }
            results[agent]["OVERALL"] = overall
            
    with open("experiments/v010_benchmark_full.json", "w") as f:
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer): return int(obj)
                if isinstance(obj, np.floating): return float(obj)
                if isinstance(obj, np.ndarray): return obj.tolist()
                return super(NpEncoder, self).default(obj)
        json.dump(results, f, indent=2, cls=NpEncoder)
        
    print("Benchmark complete. Data saved to experiments/v010_benchmark_full.json")
    for agent in AGENTS:
        print(f"{agent} Mean Final Bank: ${results[agent]['OVERALL']['mean']['final_money']:.2f}")

if __name__ == "__main__":
    main()
