"""
Standalone Industrial Livestock (V021-B) Functional Audit & Telemetry Validation
================================================================================
Validates functioning V021-B (agents/v021_b_industrial_livestock.py) vs:
- Random
- V022-C Control
- V023-G Champion
- V025-A New Leader
Across 50 paired seeds (100 games per matchup).
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

def run_match_telemetry(args):
    s, ind_path, opp_path, opp_name = args
    ind_agent = get_agent_from_path(ind_path)
    opp_agent = get_agent_from_path(opp_path)
    
    # P0 Match
    env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env0.run([ind_agent, opp_agent])
    p0_ind_r = float(env0.steps[-1][0]["reward"])
    p0_opp_r = float(env0.steps[-1][1]["reward"])
    
    # Extract end of game telemetry for V021-B in P0
    f0 = env0.steps[-1][0]["observation"]["farms"][0]
    p0_cows = sum(1 for r in f0["tiles"] for t in r if isinstance(t, dict) and t.get("animal") == "COW")
    p0_sheep = sum(1 for r in f0["tiles"] for t in r if isinstance(t, dict) and t.get("animal") == "SHEEP")
    p0_pastures = sum(1 for r in f0["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PASTURE")
    p0_straw = sum(1 for r in f0["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY")
    p0_wheat = sum(1 for r in f0["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT")
    
    # P1 Match
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([opp_agent, ind_agent])
    p1_opp_r = float(env1.steps[-1][0]["reward"])
    p1_ind_r = float(env1.steps[-1][1]["reward"])
    
    f1 = env1.steps[-1][1]["observation"]["farms"][1]
    p1_cows = sum(1 for r in f1["tiles"] for t in r if isinstance(t, dict) and t.get("animal") == "COW")
    p1_sheep = sum(1 for r in f1["tiles"] for t in r if isinstance(t, dict) and t.get("animal") == "SHEEP")
    p1_pastures = sum(1 for r in f1["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PASTURE")
    p1_straw = sum(1 for r in f1["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY")
    p1_wheat = sum(1 for r in f1["tiles"] for t in r if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT")
    
    return {
        "seed": s,
        "opp": opp_name,
        "p0_ind": p0_ind_r,
        "p0_opp": p0_opp_r,
        "p1_ind": p1_ind_r,
        "p1_opp": p1_opp_r,
        "avg_cows": (p0_cows + p1_cows) / 2.0,
        "avg_sheep": (p0_sheep + p1_sheep) / 2.0,
        "avg_pastures": (p0_pastures + p1_pastures) / 2.0,
        "avg_straw": (p0_straw + p1_straw) / 2.0,
        "avg_wheat": (p0_wheat + p1_wheat) / 2.0,
    }

def main():
    seeds = list(range(4000, 4050)) # 50 seeds = 100 games per matchup
    ind_path = "agents/v021_b_industrial_livestock.py"
    
    opponents = [
        ("Random", "random"),
        ("V022-C Control", "agents/v022_c_market_batching.py"),
        ("V023-G Champ", "agents/v023_g_capital_optimizer.py"),
        ("V025-A Leader", "agents/v025_a_aggressive_cows.py"),
    ]
    
    pool_size = min(8, mp.cpu_count())
    results = []
    
    print("=" * 115)
    print("FUNCTIONAL VALIDATION OF V021-B INDUSTRIAL LIVESTOCK (50 Seeds = 100 Games per Matchup)")
    print("=" * 115)
    
    with mp.Pool(processes=pool_size) as pool:
        for oname, opath in opponents:
            tasks = [(s, ind_path, opath, oname) for s in seeds]
            matches = pool.map(run_match_telemetry, tasks)
            
            i_scores = []
            o_scores = []
            wins, losses, ties = 0, 0, 0
            cows_list, sheep_list, pastures_list = [], [], []
            
            for m in matches:
                i_scores.extend([m["p0_ind"], m["p1_ind"]])
                o_scores.extend([m["p0_opp"], m["p1_opp"]])
                cows_list.append(m["avg_cows"])
                sheep_list.append(m["avg_sheep"])
                pastures_list.append(m["avg_pastures"])
                
                if m["p0_ind"] > m["p0_opp"]: wins += 1
                elif m["p0_ind"] == m["p0_opp"]: ties += 1
                else: losses += 1
                
                if m["p1_ind"] > m["p1_opp"]: wins += 1
                elif m["p1_ind"] == m["p1_opp"]: ties += 1
                else: losses += 1
                
            wr = (wins / len(i_scores)) * 100.0
            im = float(np.mean(i_scores))
            om = float(np.mean(o_scores))
            imed = float(np.median(i_scores))
            delta = im - om
            avg_cows = float(np.mean(cows_list))
            avg_sheep = float(np.mean(sheep_list))
            avg_pastures = float(np.mean(pastures_list))
            
            print(f"[V021-B Ind vs {oname:<18}] WR: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | V021-B Mean: ${im:7,.0f} | Opp Mean: ${om:7,.0f} | Delta: ${delta:+7,.0f} | Cows: {avg_cows:.1f} | Sheep: {avg_sheep:.1f} | Pastures: {avg_pastures:.1f}", flush=True)
            
            results.append({
                "opponent": oname,
                "win_rate": wr,
                "v021_b_mean": im,
                "opp_mean": om,
                "delta": delta,
                "avg_cows": avg_cows,
                "avg_sheep": avg_sheep,
                "avg_pastures": avg_pastures,
            })
            
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/v021_b_functional_validation.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved V021-B functional validation to scratch/v021_b_functional_validation.json")

if __name__ == "__main__":
    mp.freeze_support()
    main()
