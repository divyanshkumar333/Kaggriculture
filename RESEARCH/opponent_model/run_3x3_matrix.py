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
    
    policies = {
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "V097": os.path.join(agents_dir, "v097_cow_expansion_limit.py"),
        "V059_BerryFlywheel": os.path.join(agents_dir, "v059_strawberry_flywheel.py")
    }
    
    # 16 seeds = 32 matches per pair
    seeds = list(range(1000, 1016))
    
    csv_lines = ["candidate,opponent,W,T,L,win_score,win_rate,mean_cash,margin"]
    results_matrix = {}
    
    # Track transitivity edges
    # We specifically care about:
    # A = V025-A
    # B = V097
    # C = V059_BerryFlywheel
    
    print("Running 3x3 Payoff Matrix...")
    
    for c_name, c_path in policies.items():
        results_matrix[c_name] = {}
        for o_name, o_path in policies.items():
            if c_name == o_name:
                continue
                
            print(f"Matchup: {c_name} vs {o_name}")
            
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
                
                results_matrix[c_name][o_name] = win_rate
                csv_lines.append(f"{c_name},{o_name},{w},{t},{l},{win_score},{win_rate:.2f},{mean_cash:.0f},{margin:.0f}")

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
    
    # Save the payoff matrix CSV
    with open(os.path.join(reports_dir, "POLICY_PAYOFF_MATRIX.csv"), "w") as f:
        f.write("\n".join(csv_lines))
        
    # Analyze non-transitivity
    nontransitive = False
    try:
        a_b = results_matrix["V025-A"]["V097"] > 0.5
        b_c = results_matrix["V097"]["V059_BerryFlywheel"] > 0.5
        c_a = results_matrix["V059_BerryFlywheel"]["V025-A"] > 0.5
        
        nontransitive = a_b and b_c and c_a
        
        with open(os.path.join(reports_dir, "NONTRANSITIVITY_TEST.md"), "w") as f:
            f.write("# Non-Transitivity Test\n\n")
            f.write("## Edges (Win Rates > 50%):\n")
            f.write(f"- V025-A beats V097: {a_b} ({results_matrix['V025-A']['V097']:.2f})\n")
            f.write(f"- V097 beats V059_BerryFlywheel: {b_c} ({results_matrix['V097']['V059_BerryFlywheel']:.2f})\n")
            f.write(f"- V059_BerryFlywheel beats V025-A: {c_a} ({results_matrix['V059_BerryFlywheel']['V025-A']:.2f})\n\n")
            
            if nontransitive:
                f.write("## Conclusion\n**NON-TRANSITIVE CYCLE CONFIRMED.**\n")
                f.write("A beats B, B beats C, C beats A. No single policy globally dominates.\n")
            else:
                f.write("## Conclusion\n**MATCHUP ASYMMETRY.**\n")
                f.write("This is not a pure non-transitive cycle.\n")
                
    except KeyError as e:
        print(f"Missing data for matrix: {e}")

if __name__ == "__main__":
    main()
