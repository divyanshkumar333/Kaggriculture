import os
import json
import logging
from contextlib import redirect_stdout, redirect_stderr
from kaggle_environments import make

logging.getLogger("kaggle_environments").setLevel(logging.CRITICAL)

def evaluate_match(candidate, opponent, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    try:
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([candidate, opponent])
        p0_reward = env.steps[-1][0].reward or 0
        p1_reward = env.steps[-1][1].reward or 0
        p0_win = 1 if p0_reward > p1_reward else 0.5 if p0_reward == p1_reward else 0
        
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([opponent, candidate])
        p0_rev = env.steps[-1][0].reward or 0
        p1_rev = env.steps[-1][1].reward or 0
        p1_win = 1 if p1_rev > p0_rev else 0.5 if p1_rev == p0_rev else 0
        
        # We need more granular metrics for the league
        return {
            "w": 1 if p0_win == 1 else 0,
            "t": 1 if p0_win == 0.5 else 0,
            "l": 1 if p0_win == 0 else 0,
            "cash0": p0_reward,
            "w_rev": 1 if p1_win == 1 else 0,
            "t_rev": 1 if p1_win == 0.5 else 0,
            "l_rev": 1 if p1_win == 0 else 0,
            "cash1": p1_rev,
        }
    except Exception:
        return None

def main():
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
    main_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "main.py"))
    
    # We select a subset of the baseline to avoid 169 combinations
    baselines = {
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "V051": os.path.join(agents_dir, "v051_v16_lookahead30_final.py"),
        "V057": os.path.join(agents_dir, "v057_generalized_spoiler.py"),
        "V014": os.path.join(agents_dir, "014_robust_trace.py"),
        "V032": main_py_path,
        "V085": os.path.join(agents_dir, "v085_grandmaster_roi.py"),
        "V095": os.path.join(agents_dir, "v095_5cow_opening.py")
    }
    
    seeds = [42] # Fast smoke test
    
    csv_lines = ["candidate,opponent,W,T,L,win_score,win_rate,mean_cash,margin"]
    
    for c_name, c_path in baselines.items():
        if not os.path.exists(c_path): continue
        for o_name, o_path in baselines.items():
            if c_name == o_name or not os.path.exists(o_path): continue
            
            w, t, l = 0, 0, 0
            cash_sum = 0
            margin_sum = 0
            
            for s in seeds:
                res = evaluate_match(c_path, o_path, s)
                if res:
                    w += res["w"] + res["w_rev"]
                    t += res["t"] + res["t_rev"]
                    l += res["l"] + res["l_rev"]
                    cash_sum += res["cash0"] + res["cash1"]
                    margin_sum += (res["cash0"] - res["cash1"]) if res["w"] else (res["cash1"] - res["cash0"])
            
            total = w + t + l
            if total > 0:
                win_score = w + 0.5 * t
                win_rate = win_score / total
                mean_cash = cash_sum / total
                margin = margin_sum / total
                
                csv_lines.append(f"{c_name},{o_name},{w},{t},{l},{win_score},{win_rate:.2f},{mean_cash:.0f},{margin:.0f}")

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports", "baseline_league.csv"))
    with open(out_path, "w") as f:
        f.write("\n".join(csv_lines))

if __name__ == "__main__":
    main()
