import os
import sys
import random
import time
import subprocess
import json

V104_PATH = r"e:\Setup\kaggle\kaggriculture\submission_v104_quote_priority.py"
SCRATCH_DIR = r"e:\Setup\kaggle\kaggriculture\scratch"

def mutate_params(base_params):
    p = base_params.copy()
    mutations = random.randint(1, 2)
    for _ in range(mutations):
        k = random.choice(list(p.keys()))
        if k == "_CA_MARGIN":
            p[k] += random.choice([-5.0, 5.0, -2.5, 2.5])
        elif k == "_CA_FROM":
            p[k] += random.choice([-2, -1, 1, 2])
            p[k] = max(2, p[k])
        elif k == "_CA_TO":
            p[k] += random.choice([-2, -1, 1, 2])
        elif k == "_CA_BUFFER":
            p[k] += random.choice([-2, -1, 1, 2])
            p[k] = max(0, p[k])
        elif k == "_CA_CASH":
            p[k] += random.choice([-200, -100, 100, 200])
            p[k] = max(0, p[k])
        elif k == "_CA_FEED_DAYS":
            p[k] += random.choice([-1, 1])
            p[k] = max(0, p[k])
    return p

def run_search():
    with open(V104_PATH, "r", encoding="utf-8") as f:
        v104_code = f.read()

    base_params = {
        "_CA_FROM": 6,
        "_CA_TO": 28,
        "_CA_MARGIN": -5.0,
        "_CA_BUFFER": 8,
        "_CA_FEED_DAYS": 2,
        "_CA_CASH": 800
    }

    best_params = base_params.copy()
    
    print("Starting parameter search vs V104...", flush=True)

    for i in range(20):
        # Mutate
        cand_params = mutate_params(best_params)
        print(f"\n--- Iteration {i+1} ---", flush=True)
        print(f"Testing params: {cand_params}", flush=True)

        cand_code = v104_code
        for k, v in cand_params.items():
            if isinstance(v, float):
                cand_code = cand_code.replace(f"{k} = {base_params[k]}", f"{k} = {v}")
            else:
                cand_code = cand_code.replace(f"{k} = {base_params[k]}", f"{k} = {v}")
                
        # Hacky fix: the replace above might not match if base_params isn't what's in the text. 
        # But we know V104 has exactly those strings. Wait, if we replace in V104_code directly every time, we should replace the original values.
        cand_code = v104_code
        for k, v in cand_params.items():
            # Find the line like `_CA_MARGIN = -5.0`
            # and replace it. Since we are doing it on fresh v104_code, we replace the original literal.
            orig_val = {
                "_CA_FROM": 6,
                "_CA_TO": 28,
                "_CA_MARGIN": -5.0,
                "_CA_BUFFER": 8,
                "_CA_FEED_DAYS": 2,
                "_CA_CASH": 800
            }[k]
            cand_code = cand_code.replace(f"{k} = {orig_val}", f"{k} = {v}")

        cand_path = os.path.join(SCRATCH_DIR, f"cand_{i}.py")
        with open(cand_path, "w", encoding="utf-8") as f:
            f.write(cand_code)

        # 20 seeds = 40 games
        seeds = 20
        subprocess.run([sys.executable, "scripts/test_pair.py", cand_path, V104_PATH, str(seeds)], check=True)
        with open(os.path.join(SCRATCH_DIR, "result.json"), "r") as f:
            res = json.load(f)
        
        wins = res["wins"]
        losses = res["losses"]
        overall_margin = res["margin"]
        
        print(f"Result: {wins}W - {losses}L. Margin: {overall_margin:.1f}", flush=True)
        
        if wins > losses and (wins - losses) >= 3:
            print("Promoting to 50-seed test...", flush=True)
            subprocess.run([sys.executable, "scripts/test_pair.py", cand_path, V104_PATH, "50"], check=True)
            with open(os.path.join(SCRATCH_DIR, "result.json"), "r") as f:
                res100 = json.load(f)
            w100 = res100["wins"]
            l100 = res100["losses"]
            print(f"100-seed Result: {w100}W - {l100}L.", flush=True)
            
            if w100 > l100:
                print(f"!!! NEW BEST PARAMS !!! : {cand_params}", flush=True)
                best_params = cand_params

if __name__ == '__main__':
    run_search()
