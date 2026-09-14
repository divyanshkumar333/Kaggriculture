"""
High-Performance Paired-Game Tournament Benchmark Harness for Kaggriculture
----------------------------------------------------------------------------
Implements the multi-stage benchmark standard:
- Stage 1: 100 paired fresh games (200 matches)
- Stage 2: 500 paired fresh games (1,000 matches)
- Stage 3: 1,000+ paired fresh games (2,000+ matches)

Always tests BOTH seat positions (P0 and P1) for every seed.
Audits status for ERRORS, TIMEOUTS, INVALID actions.
Calculates:
- Match Win Rate (across all 2N games)
- Paired Win Rate (across N seeds, net delta > 0)
- Mean, Median, P10, P90, Min, Max cash for both agents
- Net cash margin
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import json
import importlib.util
from pathlib import Path
import numpy as np
import concurrent.futures
from kaggle_environments import make

def load_agent(filepath):
    abs_path = os.path.abspath(filepath)
    mod_name = f"agent_mod_{abs(hash(abs_path))}_{os.path.basename(filepath).replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def run_single_match(args):
    seed, path_p0, path_p1, label_p0, label_p1 = args
    try:
        agent_p0 = load_agent(path_p0)
        agent_p1 = load_agent(path_p1)
        
        t0 = time.time()
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([agent_p0, agent_p1])
        dt = time.time() - t0
        
        s0 = env.steps[-1][0]
        s1 = env.steps[-1][1]
        
        r0 = float(s0.reward if s0.reward is not None else 0.0)
        r1 = float(s1.reward if s1.reward is not None else 0.0)
        
        status0 = s0.status
        status1 = s1.status
        
        has_error = (status0 not in ["DONE"]) or (status1 not in ["DONE"])
        
        return {
            "seed": seed,
            "p0_label": label_p0,
            "p1_label": label_p1,
            "r0": r0,
            "r1": r1,
            "status0": status0,
            "status1": status1,
            "has_error": has_error,
            "duration": dt
        }
    except Exception as e:
        return {
            "seed": seed,
            "p0_label": label_p0,
            "p1_label": label_p1,
            "r0": 0.0,
            "r1": 0.0,
            "status0": "EXCEPTION",
            "status1": "EXCEPTION",
            "has_error": True,
            "error_msg": str(e),
            "duration": 0.0
        }

def run_paired_tournament(agent_a_path, agent_b_path, seeds, label_a="Candidate", label_b="Baseline", max_workers=6):
    print(f"=== Starting Tournament: {label_a} vs {label_b} ({len(seeds)} paired seeds = {2*len(seeds)} matches) ===", flush=True)
    t_start = time.time()
    
    tasks = []
    for s in seeds:
        # Match 1: A as P0, B as P1
        tasks.append((s, agent_a_path, agent_b_path, label_a, label_b))
        # Match 2: B as P0, A as P1
        tasks.append((s, agent_b_path, agent_a_path, label_b, label_a))
        
    results_by_seed = {}
    total_completed = 0
    errors_a = 0
    errors_b = 0
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_match, task): task for task in tasks}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            s = res["seed"]
            if s not in results_by_seed:
                results_by_seed[s] = {}
                
            if res["p0_label"] == label_a:
                results_by_seed[s]["match_a0_b1"] = res
                if res["status0"] not in ["DONE"]: errors_a += 1
                if res["status1"] not in ["DONE"]: errors_b += 1
            else:
                results_by_seed[s]["match_b0_a1"] = res
                if res["status0"] not in ["DONE"]: errors_b += 1
                if res["status1"] not in ["DONE"]: errors_a += 1
                
            total_completed += 1
            if total_completed % 20 == 0 or total_completed == len(tasks):
                print(f"  Progress: {total_completed}/{len(tasks)} matches completed ({time.time()-t_start:.1f}s)", flush=True)
                
    # Aggregate statistics
    a_cash_all = []
    b_cash_all = []
    a_wins_match = 0
    b_wins_match = 0
    ties_match = 0
    
    paired_deltas = []
    a_wins_paired = 0
    b_wins_paired = 0
    ties_paired = 0
    
    for s in seeds:
        m1 = results_by_seed[s]["match_a0_b1"]
        m2 = results_by_seed[s]["match_b0_a1"]
        
        # Match 1
        r_a1 = m1["r0"]
        r_b1 = m1["r1"]
        a_cash_all.append(r_a1)
        b_cash_all.append(r_b1)
        if r_a1 > r_b1: a_wins_match += 1
        elif r_b1 > r_a1: b_wins_match += 1
        else: ties_match += 1
        
        # Match 2
        r_b2 = m2["r0"]
        r_a2 = m2["r1"]
        a_cash_all.append(r_a2)
        b_cash_all.append(r_b2)
        if r_a2 > r_b2: a_wins_match += 1
        elif r_b2 > r_a2: b_wins_match += 1
        else: ties_match += 1
        
        # Paired delta: (a1 - b1) + (a2 - b2)
        p_delta = (r_a1 - r_b1) + (r_a2 - r_b2)
        paired_deltas.append(p_delta)
        if p_delta > 0: a_wins_paired += 1
        elif p_delta < 0: b_wins_paired += 1
        else: ties_paired += 1
        
    a_cash_arr = np.array(a_cash_all)
    b_cash_arr = np.array(b_cash_all)
    p_deltas_arr = np.array(paired_deltas)
    
    total_matches = len(a_cash_all)
    n_pairs = len(seeds)
    elapsed = time.time() - t_start
    
    summary = {
        "candidate": label_a,
        "baseline": label_b,
        "candidate_path": str(agent_a_path),
        "baseline_path": str(agent_b_path),
        "pairs": n_pairs,
        "total_matches": total_matches,
        "elapsed_seconds": round(elapsed, 1),
        "match_record": {
            "a_wins": a_wins_match,
            "b_wins": b_wins_match,
            "ties": ties_match,
            "win_rate": round(a_wins_match / total_matches, 4)
        },
        "paired_record": {
            "a_wins": a_wins_paired,
            "b_wins": b_wins_paired,
            "ties": ties_paired,
            "win_rate": round(a_wins_paired / n_pairs, 4),
            "mean_paired_delta": round(float(np.mean(p_deltas_arr)), 1),
            "median_paired_delta": round(float(np.median(p_deltas_arr)), 1)
        },
        "cash_stats": {
            label_a: {
                "mean": round(float(np.mean(a_cash_arr)), 1),
                "median": round(float(np.median(a_cash_arr)), 1),
                "p10": round(float(np.percentile(a_cash_arr, 10)), 1),
                "p90": round(float(np.percentile(a_cash_arr, 90)), 1),
                "min": round(float(np.min(a_cash_arr)), 1),
                "max": round(float(np.max(a_cash_arr)), 1),
            },
            label_b: {
                "mean": round(float(np.mean(b_cash_arr)), 1),
                "median": round(float(np.median(b_cash_arr)), 1),
                "p10": round(float(np.percentile(b_cash_arr, 10)), 1),
                "p90": round(float(np.percentile(b_cash_arr, 90)), 1),
                "min": round(float(np.min(b_cash_arr)), 1),
                "max": round(float(np.max(b_cash_arr)), 1),
            },
            "net_mean_delta": round(float(np.mean(a_cash_arr) - np.mean(b_cash_arr)), 1)
        },
        "failures": {
            f"errors_{label_a}": errors_a,
            f"errors_{label_b}": errors_b
        }
    }
    
    print("\n" + "="*60, flush=True)
    print(f"RESULTS: {label_a} vs {label_b} ({n_pairs} pairs, {total_matches} matches in {elapsed:.1f}s)", flush=True)
    print("="*60, flush=True)
    print(f"Match Win Rate:  {summary['match_record']['win_rate']*100:.1f}% ({a_wins_match}W / {b_wins_match}L / {ties_match}T)", flush=True)
    print(f"Paired Win Rate: {summary['paired_record']['win_rate']*100:.1f}% ({a_wins_paired}W / {b_wins_paired}L / {ties_paired}T)", flush=True)
    print(f"Mean Paired Delta: ${summary['paired_record']['mean_paired_delta']:+,.0f}", flush=True)
    print(f"Mean Cash:       {label_a}: ${summary['cash_stats'][label_a]['mean']:,.0f} | {label_b}: ${summary['cash_stats'][label_b]['mean']:,.0f} (Net: ${summary['cash_stats']['net_mean_delta']:+,.0f})", flush=True)
    print(f"Median Cash:     {label_a}: ${summary['cash_stats'][label_a]['median']:,.0f} | {label_b}: ${summary['cash_stats'][label_b]['median']:,.0f}", flush=True)
    print(f"P10-P90 Cash:    {label_a}: [${summary['cash_stats'][label_a]['p10']:,.0f} - ${summary['cash_stats'][label_a]['p90']:,.0f}] | {label_b}: [${summary['cash_stats'][label_b]['p10']:,.0f} - ${summary['cash_stats'][label_b]['p90']:,.0f}]", flush=True)
    print(f"Min-Max Cash:    {label_a}: [${summary['cash_stats'][label_a]['min']:,.0f} - ${summary['cash_stats'][label_a]['max']:,.0f}]", flush=True)
    print(f"Failures:        {label_a}: {errors_a} errors | {label_b}: {errors_b} errors", flush=True)
    print("="*60 + "\n", flush=True)
    
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tournament_harness.py <agent_a_path> <agent_b_path> [num_pairs=100] [label_a] [label_b]")
        sys.exit(1)
        
    path_a = sys.argv[1]
    path_b = sys.argv[2]
    num_pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    lbl_a = sys.argv[4] if len(sys.argv) > 4 else Path(path_a).stem
    lbl_b = sys.argv[5] if len(sys.argv) > 5 else Path(path_b).stem
    seed_base = int(sys.argv[6]) if len(sys.argv) > 6 else 1000
    seeds = [seed_base + i for i in range(num_pairs)]
    
    res = run_paired_tournament(path_a, path_b, seeds, label_a=lbl_a, label_b=lbl_b)
    
    out_dir = Path("RESEARCH/benchmark_history")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{lbl_a}_vs_{lbl_b}_{num_pairs}p_{int(time.time())}.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Saved benchmark results to {out_file}")
