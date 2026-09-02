"""
Phase 7: Policy Comparison (V023-E vs V023-G vs V023-H vs V022-C)
-----------------------------------------------------------------
Evaluates 3 policy variations against V022-C on fresh seeds (1100..1119).
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
    
    spec_o = importlib.util.spec_from_file_location("o", opp_path)
    mod_o = importlib.util.module_from_spec(spec_o)
    spec_o.loader.exec_module(mod_o)
    
    # P0
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env.run([mod_c.agent, mod_o.agent])
    r0, r1 = env.steps[-1][0]["reward"], env.steps[-1][1]["reward"]
    
    # P1
    env2 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env2.run([mod_o.agent, mod_c.agent])
    r0_2, r1_2 = env2.steps[-1][0]["reward"], env2.steps[-1][1]["reward"]
    
    return {
        "seed": s,
        "cand": cand_name,
        "opp": opp_name,
        "p0_score": float(r0), "p0_opp": float(r1),
        "p1_score": float(r1_2), "p1_opp": float(r0_2),
    }

if __name__ == "__main__":
    mp.freeze_support()
    seeds = list(range(1100, 1120)) # 20 seeds * 2 positions = 40 games per matchup
    
    candidates = [
        ("V023-E Fixed Cows-First", "agents/v023_e_cows_first_flywheel.py"),
        ("V023-G Capital Optimizer", "agents/v023_g_capital_optimizer.py"),
        ("V023-H Hybrid Allocator", "agents/v023_h_hybrid_flywheel.py"),
    ]
    opp_path = "agents/v022_c_market_batching.py"
    opp_name = "V022-C Control"
    
    results = {}
    with mp.Pool(processes=min(8, mp.cpu_count())) as pool:
        for cname, cpath in candidates:
            tasks = [(s, cpath, opp_path, cname, opp_name) for s in seeds]
            match_res = pool.map(run_matchup, tasks)
            
            c_scores = []
            o_scores = []
            wins = 0
            losses = 0
            ties = 0
            for m in match_res:
                c_scores.extend([m["p0_score"], m["p1_score"]])
                o_scores.extend([m["p0_opp"], m["p1_opp"]])
                if m["p0_score"] > m["p0_opp"]: wins += 1
                elif m["p0_score"] == m["p0_opp"]: ties += 1
                else: losses += 1
                
                if m["p1_score"] > m["p1_opp"]: wins += 1
                elif m["p1_score"] == m["p1_opp"]: ties += 1
                else: losses += 1
                
            wr = (wins / len(c_scores)) * 100.0
            cm = np.mean(c_scores)
            om = np.mean(o_scores)
            cmed = np.median(c_scores)
            cmin = np.min(c_scores)
            cmax = np.max(c_scores)
            
            print(f"{cname:<26} vs V022-C: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | Cand Mean: ${cm:7,.0f} | Opp Mean: ${om:7,.0f} | Min: ${cmin:7,.0f} | Max: ${cmax:7,.0f} | Margin: ${cm-om:+7,.0f}")
            results[cname] = {
                "win_rate": wr, "wins": wins, "losses": losses, "ties": ties,
                "cand_mean": float(cm), "opp_mean": float(om), "cand_median": float(cmed),
                "cand_min": float(cmin), "cand_max": float(cmax), "margin": float(cm - om)
            }
            
    with open("scratch/phase7_policy_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved Phase 7 results to scratch/phase7_policy_results.json")
