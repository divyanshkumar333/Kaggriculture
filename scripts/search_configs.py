import os
import json
import random
from typing import Dict
import subprocess
import sys

def generate_offline_score(params: Dict[str, int]) -> float:
    with open("temp_search_config.json", "w") as f:
        json.dump(params, f)
        
    env = os.environ.copy()
    env["SEARCH_CONFIG_FILE"] = "temp_search_config.json"
    
    result = subprocess.run([sys.executable, "scripts\\offline_planner.py", "--eval-only"], capture_output=True, text=True, env=env)
    
    cash = 0.0
    for line in result.stdout.split('\n'):
        if line.startswith("-> Final Cash:"):
            try:
                cash = float(line.split(":")[1].strip())
            except ValueError:
                pass
    return cash

def mutate(params: Dict[str, int]) -> Dict[str, int]:
    new_params = dict(params)
    keys = list(new_params.keys())
    k = random.choice(keys)
    delta = random.choice([-2, -1, 1, 2])
    new_params[k] = max(0, new_params[k] + delta)
    
    # Cap total plants/animals to avoid unrealistic configs
    if k in ["cow_cap", "sheep_cap", "goose_cap"]:
        new_params[k] = min(new_params[k], 20)
    else:
        new_params[k] = min(new_params[k], 80)
    
    return new_params

def main():
    print("Starting Evolutionary Search...")
    # Baseline configuration (158k Bot Premium Heavy)
    best_params = {"melon_cap": 19, "straw_cap": 36, "carrot_cap": 0, "wheat_cap": 100, "cow_cap": 9, "sheep_cap": 4, "goose_cap": 0}
    
    best_score = generate_offline_score(best_params)
    print(f"Baseline Score (Animal Heavy): {best_score}")
    
    for generation in range(50):
        candidate = mutate(best_params)
        score = generate_offline_score(candidate)
        
        if score > best_score:
            print(f"Gen {generation}: New Best! {score} | Config: {candidate}", flush=True)
            best_score = score
            best_params = candidate
        else:
            print(f"Gen {generation}: Rejected {score}", flush=True)

    print(f"\nFinal Best Config: {best_params} with score {best_score}", flush=True)

if __name__ == "__main__":
    main()
