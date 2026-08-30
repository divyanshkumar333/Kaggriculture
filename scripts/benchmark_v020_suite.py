from kaggle_environments import make
import importlib.util
import numpy as np
import json
import time

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

def run_matchup(agent_a_path, agent_b_path, seeds=[100, 101, 102, 103, 104, 105]):
    agent_a_fn = load_agent(agent_a_path)
    agent_b_fn = load_agent(agent_b_path)
    
    results = []
    for i, s in enumerate(seeds):
        # Alternate sides
        p0_is_a = (i % 2 == 0)
        agents = [agent_a_fn, agent_b_fn] if p0_is_a else [agent_b_fn, agent_a_fn]
        
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run(agents)
        
        final = env.steps[-1]
        a_idx = 0 if p0_is_a else 1
        b_idx = 1 if p0_is_a else 0
        
        reward_a = float(final[a_idx].reward or 0)
        reward_b = float(final[b_idx].reward or 0)
        
        # Determine winner
        if reward_a > reward_b:
            outcome = "WIN"
        elif reward_a < reward_b:
            outcome = "LOSS"
        else:
            outcome = "TIE"
            
        results.append({
            "seed": s,
            "reward_a": reward_a,
            "reward_b": reward_b,
            "outcome": outcome,
            "p0_is_a": p0_is_a
        })
        
    wins = sum(1 for r in results if r["outcome"] == "WIN")
    losses = sum(1 for r in results if r["outcome"] == "LOSS")
    ties = sum(1 for r in results if r["outcome"] == "TIE")
    total = len(results)
    
    banks_a = [r["reward_a"] for r in results]
    banks_b = [r["reward_b"] for r in results]
    
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "total": total,
        "win_rate": (wins / total) * 100,
        "mean_a": float(np.mean(banks_a)),
        "median_a": float(np.median(banks_a)),
        "min_a": float(np.min(banks_a)),
        "max_a": float(np.max(banks_a)),
        "mean_b": float(np.mean(banks_b)),
        "delta": float(np.mean(banks_a) - np.mean(banks_b)),
        "results": results
    }

if __name__ == "__main__":
    print("V020 Benchmark Suite Loaded.")
