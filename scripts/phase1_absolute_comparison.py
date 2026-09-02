"""
Phase 1: Direct Absolute Economic Comparison (V022-C vs V023-E)
--------------------------------------------------------------
Runs 100 paired fresh seeds (1000..1099) vs Random baseline using 8 worker processes.
Records detailed day-by-day metrics, percentiles, and paired deltas.
"""

import importlib.util
import json
import multiprocessing as mp
import numpy as np
from kaggle_environments import make

CHECKPOINT_DAYS = [5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 29]

def simulate_seed(args):
    seed, agent_path, agent_name = args
    spec = importlib.util.spec_from_file_location("ag", agent_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod.agent, "random"])
    
    day_metrics = {}
    for d in CHECKPOINT_DAYS:
        s = min(d * 24 + 23, len(env.steps) - 1)
        obs = env.steps[s][0]["observation"]
        f = obs["farms"][0]
        p = obs["private"]
        
        cows = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "COW")
        sheep = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "SHEEP")
        strawberries = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("crop") == "STRAWBERRY")
        melons = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("crop") == "MELON")
        wheat = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("crop") == "WHEAT")
        
        unsold_inv = dict(p["shed"])
        
        day_metrics[f"D{d}"] = {
            "bank": f["money"],
            "cows": cows,
            "sheep": sheep,
            "strawberries": strawberries,
            "melons": melons,
            "wheat": wheat,
            "workers": len(f["hands"]) + 1,
            "unlocked_quads": len(f["unlocked_quadrants"]),
            "shed": unsold_inv
        }
        
    final_bank = env.steps[-1][0]["reward"]
    return {
        "seed": seed,
        "agent": agent_name,
        "final_bank": float(final_bank),
        "checkpoints": day_metrics
    }

if __name__ == "__main__":
    mp.freeze_support()
    seeds = list(range(1000, 1100)) # 100 seeds
    
    tasks_v22 = [(s, "agents/v022_c_market_batching.py", "V022-C") for s in seeds]
    tasks_v23e = [(s, "agents/v023_e_cows_first_flywheel.py", "V023-E") for s in seeds]
    
    with mp.Pool(processes=min(8, mp.cpu_count())) as pool:
        print("Running V022-C across 100 seeds...")
        res_v22 = pool.map(simulate_seed, tasks_v22)
        print("Running V023-E across 100 seeds...")
        res_v23e = pool.map(simulate_seed, tasks_v23e)
        
    v22_banks = [r["final_bank"] for r in res_v22]
    v23e_banks = [r["final_bank"] for r in res_v23e]
    paired_deltas = [e - c for e, c in zip(v23e_banks, v22_banks)]
    
    def calc_stats(arr):
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "P10": float(np.percentile(arr, 10)),
            "P25": float(np.percentile(arr, 25)),
            "P50": float(np.percentile(arr, 50)),
            "P75": float(np.percentile(arr, 75)),
            "P90": float(np.percentile(arr, 90)),
        }
        
    stats_v22 = calc_stats(v22_banks)
    stats_v23e = calc_stats(v23e_banks)
    stats_deltas = calc_stats(paired_deltas)
    
    wins_e = sum(1 for d in paired_deltas if d > 0)
    ties = sum(1 for d in paired_deltas if d == 0)
    losses_e = sum(1 for d in paired_deltas if d < 0)
    
    print("\n" + "="*80)
    print("PHASE 1 ABSOLUTE ECONOMIC COMPARISON (100 PAIRED SEEDS: 1000..1099)")
    print("="*80)
    print(f"{'Metric':<10} | {'V022-C Control':<15} | {'V023-E Candidate':<15} | {'Paired Delta (E - C)':<15}")
    print("-"*80)
    for k in ["mean", "median", "std", "min", "P10", "P25", "P50", "P75", "P90", "max"]:
        print(f"{k:<10} | ${stats_v22[k]:13,.1f} | ${stats_v23e[k]:13,.1f} | ${stats_deltas[k]:+13,.1f}")
    print("-"*80)
    print(f"Paired Win Rate: {wins_e}% Wins ({wins_e}W / {losses_e}L / {ties}T) on identical seed environments")
    
    # Checkpoint trajectories
    print("\n" + "="*80)
    print("DAY-BY-DAY MEAN TRAJECTORY COMPARISON")
    print("="*80)
    print(f"{'Day':<5} | {'V022-C Bank':<12} | {'V22 Cows':<9} | {'V22 Straw':<9} | {'V023-E Bank':<12} | {'V23 Cows':<9} | {'V23 Straw':<9} | {'Delta':<10}")
    print("-"*80)
    trajectory_data = {}
    for d in CHECKPOINT_DAYS:
        key = f"D{d}"
        v22_b_mean = np.mean([r["checkpoints"][key]["bank"] for r in res_v22])
        v22_c_mean = np.mean([r["checkpoints"][key]["cows"] for r in res_v22])
        v22_s_mean = np.mean([r["checkpoints"][key]["strawberries"] for r in res_v22])
        
        v23_b_mean = np.mean([r["checkpoints"][key]["bank"] for r in res_v23e])
        v23_c_mean = np.mean([r["checkpoints"][key]["cows"] for r in res_v23e])
        v23_s_mean = np.mean([r["checkpoints"][key]["strawberries"] for r in res_v23e])
        
        delta = v23_b_mean - v22_b_mean
        print(f"Day {d:<2} | ${v22_b_mean:10,.0f} | {v22_c_mean:7.1f}   | {v22_s_mean:7.1f}   | ${v23_b_mean:10,.0f} | {v23_c_mean:7.1f}   | {v23_s_mean:7.1f}   | ${delta:+9,.0f}")
        trajectory_data[key] = {
            "v22_bank": float(v22_b_mean), "v22_cows": float(v22_c_mean), "v22_strawberries": float(v22_s_mean),
            "v23_bank": float(v23_b_mean), "v23_cows": float(v23_c_mean), "v23_strawberries": float(v23_s_mean),
            "delta": float(delta)
        }
        
    output_data = {
        "stats_v22": stats_v22,
        "stats_v23e": stats_v23e,
        "stats_deltas": stats_deltas,
        "paired_win_rate": {"wins": wins_e, "losses": losses_e, "ties": ties},
        "trajectory": trajectory_data,
        "raw_v22": res_v22,
        "raw_v23e": res_v23e
    }
    
    with open("scratch/phase1_absolute_comparison.json", "w") as f:
        json.dump(output_data, f, indent=2)
    print("\nSaved full Phase 1 comparison dataset to scratch/phase1_absolute_comparison.json")
