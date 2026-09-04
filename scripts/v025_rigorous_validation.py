"""
V025 Rigorous Validation Tournament (Phase 7 Final Confirmation)
===============================================================
200 Fresh Paired Seeds (400 Games per Matchup) for V025-A Aggressive Cows vs:
- V023-G Champion Baseline
- V022-C Official Control
- V020-C Surgical Opponent
- Industrial Livestock Opponent
- Random Baseline
"""

import multiprocessing as mp
import numpy as np
import os
import json
import importlib.util
from kaggle_environments import make

AGENT_CACHE = {}

def get_agent_from_path(path):
    if path == "random":
        return "random"
    if path not in AGENT_CACHE:
        spec = importlib.util.spec_from_file_location("mod_" + os.path.basename(path), path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        AGENT_CACHE[path] = mod.agent
    return AGENT_CACHE[path]

def run_single_match(args):
    s, cand_path, opp_path, cand_name, opp_name = args
    
    cand_agent = get_agent_from_path(cand_path)
    opp_agent = get_agent_from_path(opp_path)
    
    # P0 Match
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env0.run([cand_agent, opp_agent])
    p0_cand_r = float(env0.steps[-1][0]["reward"])
    p0_opp_r = float(env0.steps[-1][1]["reward"])
    
    # P1 Match
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([opp_agent, cand_agent])
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

def run_validation():
    seeds = list(range(3000, 3200)) # 200 fresh seeds
    cand = ("V025-A Cows", "agents/v025_a_aggressive_cows.py")
    
    opponents = [
        ("V023-G Champ", "agents/v023_g_capital_optimizer.py"),
        ("V022-C Control", "agents/v022_c_market_batching.py"),
        ("V020-C Surgical", "agents/v020_c_competitive_surgical.py"),
        ("Industrial Livestock", "agents/opp_industrial_livestock.py"),
        ("Random", "random"),
    ]
    
    pool_size = min(8, mp.cpu_count())
    results = []
    
    print("="*115)
    print(f"RIGOROUS VALIDATION: V025-A vs 5 Benchmarks across 200 Fresh Paired Seeds (400 Games per Matchup)")
    print("="*115)
    
    with mp.Pool(processes=pool_size) as pool:
        for oname, opath in opponents:
            tasks = [(s, cand[1], opath, cand[0], oname) for s in seeds]
            matches = pool.map(run_single_match, tasks)
            
            c_scores = []
            o_scores = []
            wins, losses, ties = 0, 0, 0
            
            for m in matches:
                c_scores.extend([m["p0_cand"], m["p1_cand"]])
                o_scores.extend([m["p0_opp"], m["p1_opp"]])
                
                if m["p0_cand"] > m["p0_opp"]: wins += 1
                elif m["p0_cand"] == m["p0_opp"]: ties += 1
                else: losses += 1
                
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
            
            print(f"[{cand[0]:<12} vs {oname:<20}] WR: {wr:5.1f}% ({wins:3d}W/{losses:3d}L) | Mean: ${cm:7,.0f} | Median: ${cmed:7,.0f} | P10: ${p10:7,.0f} | P25: ${p25:7,.0f} | Min: ${cmin:7,.0f} | Max: ${cmax:7,.0f} | Delta: ${mean_delta:+7,.0f}", flush=True)
            
            res_dict = {
                "candidate": cand[0],
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
            results.append(res_dict)
            
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/v025_rigorous_validation.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved rigorous validation to scratch/v025_rigorous_validation.json", flush=True)

if __name__ == "__main__":
    mp.freeze_support()
    run_validation()
