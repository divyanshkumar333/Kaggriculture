import os
import json
import logging
import sys
from contextlib import redirect_stdout, redirect_stderr
from kaggle_environments import make

# Suppress all kaggle environments logging/prints
logging.getLogger("kaggle_environments").setLevel(logging.CRITICAL)

def evaluate_match(candidate, opponent, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    
    try:
        # Play as Player 0
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([candidate, opponent])
        p0_reward = env.steps[-1][0].reward or 0
        p1_reward = env.steps[-1][1].reward or 0
        p0_result = 1 if p0_reward > p1_reward else 0.5 if p0_reward == p1_reward else 0
        
        # Play as Player 1
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([opponent, candidate])
        p0_reward_rev = env.steps[-1][0].reward or 0
        p1_reward_rev = env.steps[-1][1].reward or 0
        p1_result = 1 if p1_reward_rev > p0_reward_rev else 0.5 if p1_reward_rev == p0_reward_rev else 0
        
        return p0_result + p1_result
    except Exception as e:
        return 0  # 0 on crash

def main():
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
    main_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "main.py"))
    
    candidates = {
        "V051": os.path.join(agents_dir, "v051_v16_lookahead30_final.py"),
        "V014": os.path.join(agents_dir, "014_robust_trace.py"),
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "V032/Main": main_py_path,
        "V085": os.path.join(agents_dir, "v085_grandmaster_roi.py"),
    }
    
    meta_panel = [
        os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        os.path.join(agents_dir, "v059_strawberry_flywheel.py"),
        os.path.join(agents_dir, "v070_dynamic_roi_agent.py"),
        "random"
    ]
    
    # Using 1 seed to rapidly complete this session. In a full scale run we would use 64+
    seeds = [42, 999]
    
    results = {}
    
    for c_name, c_path in candidates.items():
        if not os.path.exists(c_path):
            print(f"Skipping {c_name} - not found.")
            continue
            
        print(f"Testing {c_name}...")
        win_score = 0
        total_matches = len(meta_panel) * len(seeds) * 2
        
        for opp in meta_panel:
            for s in seeds:
                score = evaluate_match(c_path, opp, s)
                win_score += score
                
        results[c_name] = {
            "win_score": win_score,
            "total_matches": total_matches,
            "win_rate": win_score / total_matches
        }
        
    print("\nFINAL RESULTS:")
    for c_name, res in results.items():
        print(f"{c_name}: Win Score: {res['win_score']}/{res['total_matches']} ({res['win_rate']:.2f})")
        
    # Save to file
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports", "BENCHMARK_RESULTS.json"))
    with open(out_path, "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    main()
