"""
Phase 8: Large Fresh-Seed Validation Suite (200 Paired Seeds)
-------------------------------------------------------------
Evaluates Candidate V023-G across 200 fresh seeds (1200..1399) in both P0 and P1 positions
against V022-C Champion, V020-C Surgical, V021-B Industrial, and Random.
"""

import importlib.util
import json
import multiprocessing as mp
import numpy as np
from kaggle_environments import make

def run_matchup(args):
    s, cand_path, opp_path, cand_name, opp_name = args
    spec_c = importlib.util.spec_from_file_location("c", cand_path)
    mod_c = importlib.util.module_from_spec(spec_c)
    spec_c.loader.exec_module(mod_c)
    
    if opp_path == "random":
        opp_agent = "random"
    else:
        spec_o = importlib.util.spec_from_file_location("o", opp_path)
        mod_o = importlib.util.module_from_spec(spec_o)
        spec_o.loader.exec_module(mod_o)
        opp_agent = mod_o.agent
        
    # P0
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env.run([mod_c.agent, opp_agent])
    r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
    
    # P1
    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env2.run([opp_agent, mod_c.agent])
    r0_2, r1_2 = env2.steps[-1][0]["reward"], env2.steps[-1][1]["reward"]
    
    return {
        "seed": s,
        "cand": cand_name,
        "opp": opp_name,
        "p0_cand": float(r0), "p0_opp": float(r1),
        "p1_cand": float(r1_2), "p1_opp": float(r0_2),
    }

if __name__ == "__main__":
    mp.freeze_support()
    # 200 fresh seeds
    seeds = list(range(1200, 1400)) # 200 seeds * 2 positions = 400 games per matchup
    
    cand_path = "agents/v023_g_capital_optimizer.py"
    cand_name = "V023-G Capital Optimizer"
    
    opponents = [
        ("V022-C Champion", "agents/v022_c_market_batching.py"),
        ("V020-C Surgical", "agents/v020_c_competitive_surgical.py"),
        ("V021-B Industrial", "agents/v021_b_industrial_livestock.py"),
        ("Random", "random"),
    ]
    
    tournament_summary = {}
    
    print("="*100)
    print("PHASE 8: LARGE-SCALE MULTI-ADVERSARY VALIDATION (200 SEEDS: 1200..1399, 400 GAMES / MATCHUP)")
    print("="*100)
    
    with mp.Pool(processes=min(8, mp.cpu_count())) as pool:
        for oname, opath in opponents:
            tasks = [(s, cand_path, opath, cand_name, oname) for s in seeds]
            match_res = pool.map(run_matchup, tasks)
            
            c_scores = []
            o_scores = []
            wins, losses, ties = 0, 0, 0
            
            for m in match_res:
                c_scores.extend([m["p0_cand"], m["p1_cand"]])
                o_scores.extend([m["p0_opp"], m["p1_opp"]])
                
                if m["p0_cand"] > m["p0_opp"]: wins += 1
                elif m["p0_cand"] == m["p0_opp"]: ties += 1
                else: losses += 1
                
                if m["p1_cand"] > m["p1_opp"]: wins += 1
                elif m["p1_cand"] == m["p1_opp"]: ties += 1
                else: losses += 1
                
            wr = (wins / len(c_scores)) * 100.0
            cm = np.mean(c_scores)
            om = np.mean(o_scores)
            cmed = np.median(c_scores)
            cmin = np.min(c_scores)
            cmax = np.max(c_scores)
            p10 = np.percentile(c_scores, 10)
            p25 = np.percentile(c_scores, 25)
            paired_deltas = [c - o for c, o in zip(c_scores, o_scores)]
            mean_delta = np.mean(paired_deltas)
            
            print(f"{cand_name:<25} vs {oname:<18}: WR: {wr:5.1f}% ({wins:3d}W/{losses:3d}L) | Cand Mean: ${cm:7,.0f} | Opp Mean: ${om:7,.0f} | Median: ${cmed:7,.0f} | P25: ${p25:7,.0f} | Min: ${cmin:7,.0f} | Max: ${cmax:7,.0f} | Delta: ${mean_delta:+7,.0f}")
            
            tournament_summary[oname] = {
                "win_rate": wr, "wins": wins, "losses": losses, "ties": ties,
                "cand_mean": float(cm), "opp_mean": float(om), "cand_median": float(cmed),
                "p10": float(p10), "p25": float(p25), "min": float(cmin), "max": float(cmax),
                "paired_mean_delta": float(mean_delta), "scores": [float(x) for x in c_scores]
            }
            
    with open("scratch/phase8_large_benchmark.json", "w") as f:
        json.dump(tournament_summary, f, indent=2)
    print("\nSaved Phase 8 200-seed benchmark results to scratch/phase8_large_benchmark.json")
