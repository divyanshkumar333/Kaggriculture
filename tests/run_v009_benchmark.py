import os
import sys
import json
import glob
import subprocess
import numpy as np
from collections import defaultdict

AGENTS = ["agents/v009_a_control.py", "agents/v009_b_harvest_timing.py"]
OPPONENTS = ["random", "starter", "agents/melon_maxxer.py"]
GAMES_PER_OPPONENT = 30
START_SEED = 1000

def run_experiment(agent, opponent, start_seed, games):
    print(f"Running {games} games: {agent} vs {opponent}")
    cmd = [
        sys.executable, "experiments.py",
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
        
        # Determine which file contains the agent metrics (usually p0 if we passed it as agent1)
        # We assume the agent is p0 because we pass it as agent1 in experiments.py
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
        
    # Timing metrics
    stats["late_season_seeds"] = [m.get("timing", {}).get("late_season_seeds_purchased", 0) for m in metrics_list]
    stats["late_season_plants"] = [m.get("timing", {}).get("late_season_crops_planted", 0) for m in metrics_list]
    stats["seeds_after_profitable"] = [m.get("timing", {}).get("seeds_purchased_after_profitable", 0) for m in metrics_list]
    
    stats["revenue_before_20"] = [m.get("timing", {}).get("revenue_before_20", 0) for m in metrics_list]
    stats["revenue_after_20"] = [m.get("timing", {}).get("revenue_after_20", 0) for m in metrics_list]
    
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
        "games_won": 0, # Will be calculated by experiments.json
        "count": len(metrics_list)
    }

def main():
    results = defaultdict(lambda: defaultdict(dict)) # results[agent][opponent] = stats
    
    # Store flat lists of all metrics per agent for overall stats
    agent_raw_lists = defaultdict(lambda: defaultdict(list))
    agent_wins = defaultdict(int)
    total_games = defaultdict(int)
    
    for agent in AGENTS:
        for opponent in OPPONENTS:
            run_experiment(agent, opponent, START_SEED, GAMES_PER_OPPONENT)
            metrics = collect_metrics(START_SEED, GAMES_PER_OPPONENT)
            
            # Read experiments results.json to get win rate
            win_rate = 0
            if os.path.exists("experiments/results.json"):
                with open("experiments/results.json") as f:
                    exp_data = json.load(f)
                    p1_wins = exp_data["wins_a1"]
                    win_rate = p1_wins / float(GAMES_PER_OPPONENT)
                    agent_wins[agent] += p1_wins
                    total_games[agent] += GAMES_PER_OPPONENT
            
            stats = calculate_stats(metrics)
            stats["win_rate"] = win_rate
            results[agent][opponent] = stats
            
            if stats:
                for k, v in stats["raw"].items():
                    agent_raw_lists[agent][k].extend(v)
            
    # Consolidate overall metrics per agent
    for agent in AGENTS:
        if agent_raw_lists[agent]:
            # reconstruct a dummy metrics_list so calculate_stats can do its job? 
            # No, calculate_stats takes a list of dicts. We already have the raw values.
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
                "win_rate": agent_wins[agent] / float(total_games[agent]) if total_games[agent] > 0 else 0,
                "count": total_games[agent]
            }
            results[agent]["OVERALL"] = overall
            
    # Let's save all results to a master JSON
    with open("experiments/v009_benchmark_full.json", "w") as f:
        # need to cast numpy types to python types for json serialization
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer): return int(obj)
                if isinstance(obj, np.floating): return float(obj)
                if isinstance(obj, np.ndarray): return obj.tolist()
                return super(NpEncoder, self).default(obj)
        json.dump(results, f, indent=2, cls=NpEncoder)
        
    print("Benchmark complete. Data saved to experiments/v009_benchmark_full.json")

if __name__ == "__main__":
    main()
