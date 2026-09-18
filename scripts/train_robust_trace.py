import os
import json
import base64
import zlib
import copy
import random
import time
import multiprocessing
import shutil

OPPONENTS = [
    "agents/v057_generalized_spoiler.py",
    "agents/v051_v16_lookahead30_final.py",
    "agents/v025_a_aggressive_cows.py",
    "agents/v059_strawberry_flywheel.py"
]

def load_trajectory(agent_path):
    with open(agent_path, "r") as f:
        code = f.read()
    local_env = {}
    exec(code, {}, local_env)
    return local_env["_ACTIONS"], code

def mutate_trajectory(actions, mutation_rate=0.01):
    new_actions = copy.deepcopy(actions)
    for i in range(len(new_actions)):
        if random.random() < mutation_rate:
            market = new_actions[i].get("market", [])
            if market:
                idx = random.randint(0, len(market) - 1)
                order = market[idx]
                if order and len(order) >= 3 and type(order[2]) == int:
                    order[2] = max(1, order[2] + random.choice([-2, -1, 1, 2]))
                elif order and order[0] == "HIRE":
                    if random.random() < 0.3:
                        market.pop(idx)
    return new_actions

def evaluate_match(args):
    mutant_path, opponent = args
    import subprocess
    cmd = [
        ".venv\\Scripts\\python", "-c",
        f"from kaggle_environments import make; env=make('kaggriculture', debug=False); "
        f"env.run(['{mutant_path}', '{opponent}']); "
        f"print(env.steps[-1][0].reward)"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return float(res.stdout.strip().split('\n')[-1])
    except Exception:
        return 0.0

def save_and_evaluate(base_code, new_actions, worker_id):
    compressed = zlib.compress(json.dumps(new_actions).encode('utf-8'))
    b85_str = base64.b85encode(compressed).decode('utf-8')
    
    start_idx = base_code.find('base64.b85decode(')
    first_quote = base_code.find("'", start_idx)
    last_quote = base_code.find("'", first_quote + 1)
    
    new_code = base_code[:first_quote+1] + b85_str + base_code[last_quote:]
    
    temp_path = f"scratch/mutant_{worker_id}.py"
    with open(temp_path, "w") as f:
        f.write(new_code)
        
    tasks = [(temp_path, opp) for opp in OPPONENTS]
    with multiprocessing.Pool(processes=len(OPPONENTS)) as pool:
        scores = pool.map(evaluate_match, tasks)
        
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    return avg_score, min_score, scores

def run():
    os.makedirs("scratch", exist_ok=True)
    base_actions, base_code = load_trajectory("agents/v057_generalized_spoiler.py")
    best_actions = base_actions
    best_avg, best_min, scores = save_and_evaluate(base_code, base_actions, 0)
    print(f"Baseline - Avg: {best_avg:.1f} | Min: {best_min:.1f} | Scores: {scores}")
    
    end_time = time.time() + 3600 * 3 # 3 hours
    iteration = 1
    
    while time.time() < end_time:
        new_actions = mutate_trajectory(best_actions, mutation_rate=0.01)
        avg_score, min_score, scores = save_and_evaluate(base_code, new_actions, 0)
        
        # Optimize for the MINIMUM score against any opponent (worst-case robustness)
        # combined with a small weight for average score
        fitness = min_score * 0.7 + avg_score * 0.3
        best_fitness = best_min * 0.7 + best_avg * 0.3
        
        print(f"Iter {iteration} | Avg: {avg_score:.1f} | Min: {min_score:.1f} | Scores: {scores}")
        if fitness > best_fitness:
            best_avg, best_min = avg_score, min_score
            best_actions = new_actions
            print(f"  -> NEW BEST! Fitness: {fitness:.1f}")
            shutil.copy("scratch/mutant_0.py", "agents/013_robust_trace.py")
            
        iteration += 1

if __name__ == "__main__":
    run()
