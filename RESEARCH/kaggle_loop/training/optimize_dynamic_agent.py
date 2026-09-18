import os
import random
import time
import json
import logging
from kaggle_environments import make

logging.disable(logging.WARNING)

BASE_PARAMS = {
    "HIRE_TARGETS": {0: 5, 1: 5, 2: 5, 3: 6, 4: 8, 5: 11, 6: 11, 7: 15, 8: 15, 9: 20},
    "MAX_COWS": 12,
    "MAX_STRAWBERRIES": 40,
    "MAX_MELONS": 20,
    "COW_MIN_MONEY": 500,
    "STRAW_MIN_MONEY": 250,
    "MELON_MIN_MONEY": 300,
    "SPOILER_URGENCY_THRESH": 60,
    "WEIGHT_URGENT_WATER": 2000,
    "WEIGHT_FEED_ANIMAL": 1600,
    "WEIGHT_CARE_ANIMAL": 1400,
    "WEIGHT_CLEAR_WEED": 1200,
    "WEIGHT_WATER_PLANT": 1000,
    "WEIGHT_HARVEST_LIVESTOCK": 950,
    "WEIGHT_COLLECT_FERTILIZER": 900,
    "WEIGHT_HARVEST_CROP": 850,
    "WEIGHT_BUILD_STRUCTURE": 750,
    "WEIGHT_PLACE_ANIMAL": 700,
    "WEIGHT_PLANT_SEED": 650,
}

def mutate(params):
    new_params = json.loads(json.dumps(params))
    # Mutate 2-3 random keys
    for _ in range(random.randint(2, 4)):
        k = random.choice(list(new_params.keys()))
        if k == "HIRE_TARGETS":
            # Mutate one of the days
            d = random.choice(list(new_params[k].keys()))
            new_params[k][d] += random.choice([-2, -1, 1, 2])
            new_params[k][d] = max(0, min(23, new_params[k][d]))
        elif k.startswith("MAX_"):
            new_params[k] += random.choice([-5, -2, 2, 5])
            new_params[k] = max(0, new_params[k])
        elif k.endswith("_MIN_MONEY"):
            new_params[k] += random.choice([-100, -50, 50, 100])
            new_params[k] = max(0, new_params[k])
        elif k == "SPOILER_URGENCY_THRESH":
            new_params[k] += random.choice([-10, -5, 5, 10])
            new_params[k] = max(10, new_params[k])
        elif k.startswith("WEIGHT_"):
            new_params[k] += random.choice([-200, -100, 100, 200])
            new_params[k] = max(100, new_params[k])
    return new_params

def write_agent(params, filepath):
    with open("agents/v070_dynamic_roi_agent.py", "r") as f:
        content = f.read()
    
    # Replace the PARAMS dict in the content
    import re
    # We just replace the whole string
    param_str = "PARAMS = " + json.dumps(params, indent=4)
    # Regex to find PARAMS = { ... }
    content = re.sub(r"PARAMS = \{.*?\}", param_str, content, flags=re.DOTALL)
    
    with open(filepath, "w") as f:
        f.write(content)

def evaluate(agent_path, opponent_path, num_matches=2):
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    total_score = 0
    wins = 0
    for _ in range(num_matches):
        env.reset()
        steps = env.run([agent_path, opponent_path])
        final = steps[-1]
        s1 = final[0].reward or 0
        s2 = final[1].reward or 0
        total_score += s1
        if s1 > s2:
            wins += 1
    return total_score / num_matches, wins

if __name__ == "__main__":
    best_params = BASE_PARAMS
    best_score = -1
    
    opponent = "agents/v063_meta_router.py"
    
    # Baseline
    print("Evaluating baseline...")
    write_agent(best_params, "agents/temp_agent.py")
    best_score, best_wins = evaluate("agents/temp_agent.py", opponent, 3)
    print(f"Baseline Score: {best_score} (Wins: {best_wins}/3)")
    
    for i in range(50):
        test_params = mutate(best_params)
        write_agent(test_params, "agents/temp_agent.py")
        
        t0 = time.time()
        score, wins = evaluate("agents/temp_agent.py", opponent, 2)
        t1 = time.time()
        
        print(f"Iter {i+1}: Score = {score}, Wins = {wins}/2. Time: {t1-t0:.1f}s")
        if score > best_score:
            print("NEW BEST! Score:", score)
            best_score = score
            best_params = test_params
            with open("agents/v071_optimized_dynamic.py", "w") as f:
                with open("agents/temp_agent.py", "r") as src:
                    f.write(src.read())
            
    print("Done. Best score:", best_score)
