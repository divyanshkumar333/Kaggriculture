import os
import importlib.util
from kaggle_environments import make
import pandas as pd
import numpy as np

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_benchmark():
    v022_a = load_agent("agents/v022_a_replay_opening.py")
    v020_c = load_agent("agents/v020_c_competitive_surgical.py")
    v005_d = load_agent("agents/v005_d_combined.py")
    v009_b = load_agent("agents/v009_b_harvest_timing.py")
    v004_b = load_agent("agents/v004_b_diversify.py")
    v008_d = load_agent("agents/v008_d_dynamic_clusters.py")
    opp_industrial = load_agent("agents/opp_industrial_livestock.py")
    opp_melon = load_agent("agents/opp_melon_flooder.py")
    
    opponents = [
        ("V020-C (Frozen Control)", v020_c),
        ("Industrial Livestock", opp_industrial),
        ("Animal Optimizer (V005-D)", v005_d),
        ("Harvest Timing (V009-B)", v009_b),
        ("Diversified (V004-B)", v004_b),
        ("Dynamic Clusters (V008-D)", v008_d),
        ("Melon Flooder", opp_melon),
        ("Starter", "starter"),
        ("Random", "random"),
    ]
    
    # 12 Fresh Seeds (600..611) with alternating P0/P1
    seeds = list(range(600, 612))
    
    print("==========================================================================")
    print("V022-A EXPERIMENTAL BENCHMARK SUITE")
    print("==========================================================================")
    
    overall_results = []
    
    for opp_name, opp_agent in opponents:
        opp_res = []
        for i, s in enumerate(seeds):
            p0_cand = (i % 2 == 0)
            agents = [v022_a, opp_agent] if p0_cand else [opp_agent, v022_a]
            
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
            env.run(agents)
            
            p0_rew = env.steps[-1][0]["reward"]
            p1_rew = env.steps[-1][1]["reward"]
            
            cand_rew = p0_rew if p0_cand else p1_rew
            opp_rew = p1_rew if p0_cand else p0_rew
            
            win = 1.0 if cand_rew > opp_rew else (0.5 if cand_rew == opp_rew else 0.0)
            opp_res.append({
                "seed": s,
                "cand_rew": cand_rew,
                "opp_rew": opp_rew,
                "win": win,
                "delta": cand_rew - opp_rew
            })
            overall_results.append({
                "opp": opp_name,
                "seed": s,
                "cand_rew": cand_rew,
                "opp_rew": opp_rew,
                "win": win
            })
            
        df_opp = pd.DataFrame(opp_res)
        wr = df_opp["win"].mean() * 100
        mean_c = df_opp["cand_rew"].mean()
        mean_o = df_opp["opp_rew"].mean()
        print(f"vs {opp_name:<30} | WR: {wr:>5.1f}% | Cand: ${mean_c:>8,.0f} | Opp: ${mean_o:>8,.0f} | Delta: ${mean_c-mean_o:>+8,.0f}")
        
    df_all = pd.DataFrame(overall_results)
    total_wr = df_all["win"].mean() * 100
    total_cand = df_all["cand_rew"].mean()
    total_opp = df_all["opp_rew"].mean()
    floor = df_all["cand_rew"].min()
    
    print("==========================================================================")
    print(f"OVERALL SUMMARY (108 GAMES):")
    print(f"  Field Win Rate:    {total_wr:.1f}%")
    print(f"  Mean Candidate:    ${total_cand:,.0f}")
    print(f"  Mean Opponent:     ${total_opp:,.0f}")
    print(f"  Worst-Case Floor:  ${floor:,.0f}")
    print("==========================================================================")

if __name__ == "__main__":
    run_benchmark()
