import importlib.util
import numpy as np
import time
import os
import json
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path).replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_matchup(agent_a_fn, agent_b_fn, agent_a_name, agent_b_name, seeds, turns=720):
    results = []
    
    for i, seed in enumerate(seeds):
        os.environ["KAGGRICULTURE_SEED"] = str(seed)
        
        # Alternate positions P0 and P1
        if i % 2 == 0:
            p0_fn, p1_fn = agent_a_fn, agent_b_fn
            p0_name, p1_name = agent_a_name, agent_b_name
            a_is_p0 = True
        else:
            p0_fn, p1_fn = agent_b_fn, agent_a_fn
            p0_name, p1_name = agent_b_name, agent_a_name
            a_is_p0 = False
            
        env = make("kaggriculture", configuration={"episodeSteps": turns, "seed": seed}, debug=False)
        env.run([p0_fn, p1_fn])
        
        final_step = env.steps[-1]
        p0_reward = final_step[0]["reward"] or 0.0
        p1_reward = final_step[1]["reward"] or 0.0
        
        a_reward = p0_reward if a_is_p0 else p1_reward
        b_reward = p1_reward if a_is_p0 else p0_reward
        
        a_win = a_reward > b_reward
        b_win = b_reward > a_reward
        tie = a_reward == b_reward
        
        results.append({
            "seed": seed,
            "a_is_p0": a_is_p0,
            "a_reward": a_reward,
            "b_reward": b_reward,
            "a_win": a_win,
            "b_win": b_win,
            "tie": tie
        })
        
    wins_a = sum(1 for r in results if r["a_win"])
    wins_b = sum(1 for r in results if r["b_win"])
    ties = sum(1 for r in results if r["tie"])
    mean_a = np.mean([r["a_reward"] for r in results])
    mean_b = np.mean([r["b_reward"] for r in results])
    min_a = np.min([r["a_reward"] for r in results])
    median_a = np.median([r["a_reward"] for r in results])
    win_rate_a = (wins_a / len(results)) * 100
    
    return {
        "agent_a": agent_a_name,
        "agent_b": agent_b_name,
        "total_games": len(results),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "win_rate_a": win_rate_a,
        "mean_a": mean_a,
        "mean_b": mean_b,
        "min_a": min_a,
        "median_a": median_a,
        "delta": mean_a - mean_b,
        "games": results
    }

def main():
    print("================================================================================")
    print("STARTING V021-A COMPETITIVE BENCHMARK SUITE")
    print("================================================================================")
    
    # Seeds for evaluation (12 deterministic seeds)
    SEEDS = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    
    # Load candidate agents
    v020_c_fn = load_agent("agents/v020_c_competitive_surgical.py")
    v021_a_fn = load_agent("agents/v021_a_labor_throughput.py")
    
    # Load opponent pool
    opponents = {
        "V020-C (Control)": v020_c_fn,
        "Industrial Livestock": load_agent("agents/opp_industrial_livestock.py"),
        "Animal Optimizer (V005-D)": load_agent("agents/v005_d_combined.py"),
        "Diversified (V004-B)": load_agent("agents/v004_b_diversify.py"),
        "Harvest Timing (V009-B)": load_agent("agents/v009_b_harvest_timing.py"),
        "Melon Flooder": load_agent("agents/opp_melon_flooder.py"),
        "Starter": "starter",
        "Random": "random"
    }
    
    print("\n--- 1. DIRECT HEAD-TO-HEAD: V021-A vs V020-C ---")
    h2h_res = run_matchup(v021_a_fn, v020_c_fn, "V021-A", "V020-C", SEEDS)
    print(f"Result: Win Rate: {h2h_res['win_rate_a']:.1f}% ({h2h_res['wins_a']}W / {h2h_res['wins_b']}L / {h2h_res['ties']}T)")
    print(f"V021-A Mean Bank: ${h2h_res['mean_a']:,.0f} | V020-C Mean Bank: ${h2h_res['mean_b']:,.0f} | Delta: ${h2h_res['delta']:+,.0f}")
    
    # Benchmark both V020-C and V021-A across all opponent archetypes
    print("\n--- 2. FULL BENCHMARK SUITE ACROSS ALL OPPONENTS ---")
    all_summary = []
    
    for opp_name, opp_fn in opponents.items():
        if opp_name == "V020-C (Control)":
            continue
        print(f"\nEvaluating against: {opp_name}...")
        
        # Run V020-C vs Opponent
        res_c = run_matchup(v020_c_fn, opp_fn, "V020-C", opp_name, SEEDS)
        # Run V021-A vs Opponent
        res_a = run_matchup(v021_a_fn, opp_fn, "V021-A", opp_name, SEEDS)
        
        print(f"  V020-C vs {opp_name:22s} | WR: {res_c['win_rate_a']:5.1f}% ({res_c['wins_a']}W/{res_c['wins_b']}L) | Bank: ${res_c['mean_a']:6,.0f} vs ${res_c['mean_b']:6,.0f} | Min: ${res_c['min_a']:6,.0f}")
        print(f"  V021-A vs {opp_name:22s} | WR: {res_a['win_rate_a']:5.1f}% ({res_a['wins_a']}W/{res_a['wins_b']}L) | Bank: ${res_a['mean_a']:6,.0f} vs ${res_a['mean_b']:6,.0f} | Min: ${res_a['min_a']:6,.0f}")
        
        all_summary.append({
            "opponent": opp_name,
            "v020_c": res_c,
            "v021_a": res_a
        })
        
    os.makedirs("experiments", exist_ok=True)
    with open("experiments/v021_a_benchmark_results.json", "w") as f:
        json.dump({"h2h": h2h_res, "field": all_summary}, f, indent=2)
        
    print("\n================================================================================")
    print("BENCHMARK COMPLETE. Results saved to experiments/v021_a_benchmark_results.json")
    print("================================================================================")

if __name__ == "__main__":
    main()
