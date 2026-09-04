"""
V024 Succession Benchmark Suite (Phase 6 & 8)
==============================================
Runs high-throughput paired-seed tournaments across all succession candidates:
- V023-I: Control
- V023-J: Automatic Strawberry -> Wheat Succession
- V023-K: Conservative Succession
- V023-L: Economic Succession
- V023-M: Market-Aware Succession
Against:
- V023-G Champion Baseline
- V022-C Official Control
- V020-C Surgical Opponent
- V021-B Industrial Livestock
- Random Baseline
"""

import importlib.util
import json
import multiprocessing as mp
import numpy as np
import os
import pandas as pd
from kaggle_environments import make

def run_single_match(args):
    s, cand_path, opp_path, cand_name, opp_name = args
    
    spec_c = importlib.util.spec_from_file_location("cand", cand_path)
    mod_c = importlib.util.module_from_spec(spec_c)
    spec_c.loader.exec_module(mod_c)
    
    if opp_path == "random":
        opp_agent = "random"
    else:
        spec_o = importlib.util.spec_from_file_location("opp", opp_path)
        mod_o = importlib.util.module_from_spec(spec_o)
        spec_o.loader.exec_module(mod_o)
        opp_agent = mod_o.agent
        
    # P0 Match
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env0.run([mod_c.agent, opp_agent])
    p0_cand_r = float(env0.steps[-1][0]["reward"])
    p0_opp_r = float(env0.steps[-1][1]["reward"])
    
    # P1 Match
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([opp_agent, mod_c.agent])
    p1_opp_r = float(env1.steps[-1][0]["reward"])
    p1_cand_r = float(env1.steps[-1][1]["reward"])
    
    return {
        "seed": s,
        "cand": cand_name,
        "opp": opp_name,
        "p0_cand": p0_cand_r,
        "p0_opp": p0_opp_r,
        "p1_cand": p1_cand_r,
        "p1_opp": p1_opp_r,
    }

def run_tournament(candidates, opponents, seeds, pool_size=None):
    if pool_size is None:
        pool_size = min(8, mp.cpu_count())
        
    results_summary = []
    detailed_data = {}
    
    with mp.Pool(processes=pool_size) as pool:
        for cname, cpath in candidates:
            detailed_data[cname] = {}
            for oname, opath in opponents:
                tasks = [(s, cpath, opath, cname, oname) for s in seeds]
                matches = pool.map(run_single_match, tasks)
                
                c_scores = []
                o_scores = []
                wins, losses, ties = 0, 0, 0
                
                for m in matches:
                    c_scores.extend([m["p0_cand"], m["p1_cand"]])
                    o_scores.extend([m["p0_opp"], m["p1_opp"]])
                    
                    # P0 game
                    if m["p0_cand"] > m["p0_opp"]: wins += 1
                    elif m["p0_cand"] == m["p0_opp"]: ties += 1
                    else: losses += 1
                    
                    # P1 game
                    if m["p1_cand"] > m["p1_opp"]: wins += 1
                    elif m["p1_cand"] == m["p1_opp"]: ties += 1
                    else: losses += 1
                    
                total_games = len(c_scores)
                wr = (wins / total_games) * 100.0
                cm = float(np.mean(c_scores))
                om = float(np.mean(o_scores))
                cmed = float(np.median(c_scores))
                cstd = float(np.std(c_scores))
                cmin = float(np.min(c_scores))
                cmax = float(np.max(c_scores))
                p10 = float(np.percentile(c_scores, 10))
                p25 = float(np.percentile(c_scores, 25))
                p75 = float(np.percentile(c_scores, 75))
                p90 = float(np.percentile(c_scores, 90))
                deltas = [c - o for c, o in zip(c_scores, o_scores)]
                mean_delta = float(np.mean(deltas))
                
                print(f"[{cname:<10} vs {oname:<18}] WR: {wr:5.1f}% ({wins:3d}W/{losses:3d}L) | Mean: ${cm:7,.0f} | Median: ${cmed:7,.0f} | P10: ${p10:7,.0f} | P25: ${p25:7,.0f} | Min: ${cmin:7,.0f} | Max: ${cmax:7,.0f} | Delta: ${mean_delta:+7,.0f}")
                
                res_dict = {
                    "candidate": cname,
                    "opponent": oname,
                    "total_games": total_games,
                    "wins": wins,
                    "losses": losses,
                    "ties": ties,
                    "win_rate": wr,
                    "cand_mean": cm,
                    "opp_mean": om,
                    "cand_median": cmed,
                    "cand_std": cstd,
                    "p10": p10,
                    "p25": p25,
                    "p75": p75,
                    "p90": p90,
                    "min": cmin,
                    "max": cmax,
                    "paired_mean_delta": mean_delta,
                }
                results_summary.append(res_dict)
                detailed_data[cname][oname] = res_dict
                
    return results_summary, detailed_data

if __name__ == "__main__":
    mp.freeze_support()
    print("="*100)
    print("PHASE 6: 3-WAY SUCCESSION SCREENING TOURNAMENT (Seeds 1400..1449, 50 Seeds = 100 Games per matchup)")
    print("="*100)
    
    screening_seeds = list(range(1400, 1450))
    
    candidates = [
        ("V023-I (Ctrl)", "agents/v023_i_control.py"),
        ("V023-J (Auto)", "agents/v023_j_auto_succession.py"),
        ("V023-K (Cons)", "agents/v023_k_conservative.py"),
        ("V023-L (Econ)", "agents/v023_l_economic.py"),
        ("V023-M (Mkt)",  "agents/v023_m_market_aware.py"),
    ]
    
    benchmark_opponents = [
        ("V023-G Champ", "agents/v023_g_capital_optimizer.py"),
        ("V022-C Control", "agents/v022_c_market_batching.py"),
        ("Random", "random"),
    ]
    
    summary, details = run_tournament(candidates, benchmark_opponents, screening_seeds)
    
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/v024_screening_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved screening results to scratch/v024_screening_summary.json")
