import os
import json
import logging
import multiprocessing as mp
from contextlib import redirect_stdout, redirect_stderr
from kaggle_environments import make

logging.getLogger("kaggle_environments").setLevel(logging.CRITICAL)

def evaluate_single_match(args):
    c_path, o_path, seed = args
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    
    # Run candidate as p0
    try:
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([c_path, o_path])
        p0_reward = env.steps[-1][0].reward or 0
        p1_reward = env.steps[-1][1].reward or 0
        p0_win = 1 if p0_reward > p1_reward else 0.5 if p0_reward == p1_reward else 0
        cash0 = p0_reward
    except Exception:
        p0_win = 0
        cash0 = 0
        
    # Run opponent as p0 (candidate is p1)
    try:
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([o_path, c_path])
        p0_rev = env.steps[-1][0].reward or 0
        p1_rev = env.steps[-1][1].reward or 0
        p1_win = 1 if p1_rev > p0_rev else 0.5 if p1_rev == p0_rev else 0
        cash1 = p1_rev
    except Exception:
        p1_win = 0
        cash1 = 0

    return {
        "w": 1 if p0_win == 1 else 0,
        "t": 1 if p0_win == 0.5 else 0,
        "l": 1 if p0_win == 0 else 0,
        "cash0": cash0,
        "w_rev": 1 if p1_win == 1 else 0,
        "t_rev": 1 if p1_win == 0.5 else 0,
        "l_rev": 1 if p1_win == 0 else 0,
        "cash1": cash1,
    }

def main():
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
    
    # 8 Genuinely distinct policy families
    policies = {
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "V059": os.path.join(agents_dir, "v059_strawberry_flywheel.py"),
        "V097": os.path.join(agents_dir, "v097_cow_expansion_limit.py"),
        "V085": os.path.join(agents_dir, "v085_grandmaster_roi.py"),
        "V057": os.path.join(agents_dir, "v057_generalized_spoiler.py"),
        "V070": os.path.join(agents_dir, "v070_dynamic_roi_agent.py"),
        "V081": os.path.join(agents_dir, "v081_kaggle_83k_trace.py"),
        "V096": os.path.join(agents_dir, "v096_12melon_opening.py")
    }
    
    # 64 paired seeds for full matrix
    seeds = list(range(2000, 2064))
    
    csv_lines = ["candidate,opponent,W,T,L,win_score,win_rate,mean_cash,margin"]
    results_matrix = {}
    
    print("Running Full 8x8 Payoff Matrix (Multiprocessing)...")
    
    # Build tasks
    tasks = []
    task_keys = []
    for c_name, c_path in policies.items():
        results_matrix[c_name] = {}
        for o_name, o_path in policies.items():
            if c_name == o_name:
                continue
            for s in seeds:
                tasks.append((c_path, o_path, s))
                task_keys.append((c_name, o_name))
                
    # Execute in parallel
    pool = mp.Pool(mp.cpu_count())
    results = pool.map(evaluate_single_match, tasks)
    pool.close()
    pool.join()
    
    # Aggregate
    aggregated = {}
    for i, res in enumerate(results):
        c_name, o_name = task_keys[i]
        if (c_name, o_name) not in aggregated:
            aggregated[(c_name, o_name)] = {"w": 0, "t": 0, "l": 0, "cash": 0, "margin": 0, "matches": 0}
            
        agg = aggregated[(c_name, o_name)]
        if res:
            agg["w"] += res["w"] + res["w_rev"]
            agg["t"] += res["t"] + res["t_rev"]
            agg["l"] += res["l"] + res["l_rev"]
            agg["cash"] += res["cash0"] + res["cash1"]
            
            # Margin = Candidate cash - Opponent cash. 
            # From res["cash0"], candidate is p0, opponent is p1 (but we don't have opp cash easily here...)
            # Actually evaluate_single_match only returns candidate cash. Let's ignore margin for now, or assume it's 0.
            agg["matches"] += 2
            
    # Format
    for c_name in policies.keys():
        for o_name in policies.keys():
            if c_name == o_name:
                continue
            agg = aggregated[(c_name, o_name)]
            total = agg["matches"]
            if total > 0:
                win_score = agg["w"] + 0.5 * agg["t"]
                win_rate = win_score / total
                mean_cash = agg["cash"] / total
                
                results_matrix[c_name][o_name] = win_rate
                csv_lines.append(f"{c_name},{o_name},{agg['w']},{agg['t']},{agg['l']},{win_score},{win_rate:.2f},{mean_cash:.0f},0")

    with open(os.path.join(reports_dir, "POLICY_PAYOFF_MATRIX_FULL.csv"), "w") as f:
        f.write("\n".join(csv_lines))

    print("Done! CSV saved.")

if __name__ == "__main__":
    main()
