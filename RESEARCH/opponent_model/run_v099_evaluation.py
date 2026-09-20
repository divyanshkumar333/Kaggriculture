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
    
    candidate = os.path.join(agents_dir, "v099_adaptive_master.py")
    
    opponents = {
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "V059": os.path.join(agents_dir, "v059_strawberry_flywheel.py"),
        "V097": os.path.join(agents_dir, "v097_cow_expansion_limit.py"),
        "V085": os.path.join(agents_dir, "v085_grandmaster_roi.py"),
        "V057": os.path.join(agents_dir, "v057_generalized_spoiler.py"),
        "V070": os.path.join(agents_dir, "v070_dynamic_roi_agent.py"),
        "V081": os.path.join(agents_dir, "v081_kaggle_83k_trace.py"),
        "V096": os.path.join(agents_dir, "v096_12melon_opening.py")
    }
    
    seeds = list(range(3000, 3064))
    csv_lines = ["candidate,opponent,W,T,L,win_score,win_rate,mean_cash,margin"]
    aggregated = {}
    
    print("Running V099 Evaluation (Multiprocessing)...")
    
    tasks = []
    task_keys = []
    for o_name, o_path in opponents.items():
        aggregated[o_name] = {"w": 0, "t": 0, "l": 0, "cash": 0, "matches": 0}
        for s in seeds:
            tasks.append((candidate, o_path, s))
            task_keys.append(o_name)
                
    results = [evaluate_single_match(task) for task in tasks]
    
    for i, res in enumerate(results):
        o_name = task_keys[i]
        agg = aggregated[o_name]
        if res:
            agg["w"] += res["w"] + res["w_rev"]
            agg["t"] += res["t"] + res["t_rev"]
            agg["l"] += res["l"] + res["l_rev"]
            agg["cash"] += res["cash0"] + res["cash1"]
            agg["matches"] += 2
            
    total_w = total_t = total_l = 0
    
    with open(os.path.join(reports_dir, "V099_EVALUATION.md"), "w") as f:
        f.write("# V099 Adaptive Master Evaluation\n\n")
        f.write("| Opponent | Win Rate | W | T | L | Mean Cash |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for o_name in opponents.keys():
            agg = aggregated[o_name]
            total = agg["matches"]
            if total > 0:
                win_score = agg["w"] + 0.5 * agg["t"]
                win_rate = win_score / total
                mean_cash = agg["cash"] / total
                
                total_w += agg["w"]
                total_t += agg["t"]
                total_l += agg["l"]
                
                f.write(f"| {o_name} | {win_rate:.2f} | {agg['w']} | {agg['t']} | {agg['l']} | {mean_cash:.0f} |\n")
        
        total_matches = total_w + total_t + total_l
        global_wr = (total_w + 0.5 * total_t) / total_matches if total_matches > 0 else 0
        f.write(f"\n**Global Aggregate Win Rate:** {global_wr:.2f}\n")
        
    print("Done! Evaluation saved to reports/V099_EVALUATION.md")

if __name__ == "__main__":
    main()
