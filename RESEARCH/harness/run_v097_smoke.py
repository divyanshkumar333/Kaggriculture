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
        return 1 if p0_reward > p1_reward else 0.5 if p0_reward == p1_reward else 0
    except Exception:
        return 0

def main():
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
    candidate = os.path.join(agents_dir, "v097_cow_expansion_limit.py")
    
    opponents = {
        "V025-A": os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        "Strawberry-Flywheel": os.path.join(agents_dir, "v059_strawberry_flywheel.py"),
    }
    
    seeds = [42, 999] # Smoke test (2 seeds * 2 opponents * 2 seats = 8 matches)
    
    print("Smoking V097...")
    for o_name, o_path in opponents.items():
        win_score = 0
        total_matches = len(seeds) * 2
        for s in seeds:
            res_0 = evaluate_match(candidate, o_path, s)
            res_1 = evaluate_match(o_path, candidate, s)
            # res_1 is the opponent's win score when they are p0.
            # our win score is 1 - res_1 (ignoring ties for simple smoke test logic, wait...
            # if res_1 = 1, we lost, so we get 0. if res_1=0.5, we get 0.5. if res_1 = 0, we get 1.
            cand_res_1 = 1 - res_1
            win_score += res_0 + cand_res_1
            
        print(f"V097 vs {o_name}: {win_score}/{total_matches}")

if __name__ == "__main__":
    main()
