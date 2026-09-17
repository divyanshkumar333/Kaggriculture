import os
import json
import base64
import zlib
import copy
import random
import subprocess
import time

def load_trajectory(agent_path):
    # Extremely hacky way to extract _ACTIONS
    with open(agent_path, "r") as f:
        code = f.read()
    
    local_env = {}
    exec(code, {}, local_env)
    return local_env["_ACTIONS"], code

def mutate_trajectory(actions, mutation_rate=0.05):
    new_actions = copy.deepcopy(actions)
    
    for i in range(len(new_actions)):
        if random.random() < mutation_rate:
            market = new_actions[i].get("market", [])
            if not market:
                # Randomly insert a HIRE if empty (very rare to randomly be valid but we can try)
                pass
            else:
                # Mutate existing market order
                idx = random.randint(0, len(market) - 1)
                order = market[idx]
                if order and len(order) >= 3 and type(order[2]) == int:
                    # Mutate quantity by +/- 1
                    order[2] = max(1, order[2] + random.choice([-1, 1]))
                elif order and order[0] == "HIRE":
                    # Maybe remove a HIRE or move it
                    if random.random() < 0.5:
                        market.pop(idx)
    return new_actions

def save_and_evaluate(base_code, new_actions):
    # Re-encode
    compressed = zlib.compress(json.dumps(new_actions).encode('utf-8'))
    b85_str = base64.b85encode(compressed).decode('utf-8')
    
    # Replace the old base64 block
    start_idx = base_code.find('base64.b85decode(')
    first_quote = base_code.find("'", start_idx)
    last_quote = base_code.find("'", first_quote + 1)
    
    new_code = base_code[:first_quote+1] + b85_str + base_code[last_quote:]
    
    # Write to temp file
    temp_path = "experiments/005_dynamic_livestock/mutant.py"
    with open(temp_path, "w") as f:
        f.write(new_code)
        
    # Evaluate vs v057
    try:
        cmd1 = [
            ".venv\\Scripts\\python", "-c",
            "from kaggle_environments import make; env=make('kaggriculture', debug=False); "
            "env.run(['experiments/005_dynamic_livestock/mutant.py', 'agents/v057_generalized_spoiler.py']); "
            "print(env.steps[-1][0].reward)"
        ]
        res1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=15)
        score_v057 = float(res1.stdout.strip().split('\n')[-1])
        return score_v057
    except Exception:
        return 0

def run_evolution(duration_hours=2):
    print("Starting Trajectory Evolution Loop...")
    end_time = time.time() + duration_hours * 3600
    
    base_actions, base_code = load_trajectory("agents/v057_generalized_spoiler.py")
    best_actions = base_actions
    best_score = save_and_evaluate(base_code, base_actions)
    print(f"Baseline Score: {best_score}")
    
    iteration = 1
    while time.time() < end_time:
        new_actions = mutate_trajectory(best_actions, mutation_rate=0.01)
        score = save_and_evaluate(base_code, new_actions)
        
        print(f"Iter {iteration} | Score: {score}")
        if score > best_score:
            best_score = score
            best_actions = new_actions
            print(f"  -> NEW BEST SCORE: {best_score}")
            # Save the best code
            import shutil
            shutil.copy("experiments/005_dynamic_livestock/mutant.py", "RESEARCH/kaggle_loop/training/best_mutant.py")
            
        iteration += 1

if __name__ == "__main__":
    os.makedirs("experiments/005_dynamic_livestock", exist_ok=True)
    run_evolution(duration_hours=2)
