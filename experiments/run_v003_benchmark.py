import os
import json
import time
import multiprocessing
from kaggle_environments import make

def run_match(args):
    variant_name, variant_path, opp_name, opp_path, seed = args
    
    # We use a unique seed string for metrics tracking
    metrics_seed = f"{variant_name}_{opp_name}_{seed}"
    os.environ["KAGGRICULTURE_SEED"] = metrics_seed
    
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        # Variant is always P1, opponent is P2
        env.run([variant_path, opp_path])
        
        # Reward is final money
        final_state = env.steps[-1]
        p1_money = final_state[0].reward if final_state[0].reward is not None else 0
        p2_money = final_state[1].reward if final_state[1].reward is not None else 0
        
        return {
            "variant": variant_name,
            "opponent": opp_name,
            "seed": seed,
            "p1_money": p1_money,
            "p2_money": p2_money,
            "metrics_id": metrics_seed
        }
    except Exception as e:
        print(f"Error in {metrics_seed}: {e}")
        return {
            "variant": variant_name,
            "opponent": opp_name,
            "seed": seed,
            "p1_money": 0,
            "p2_money": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    variants = [
        ("v002_c", "agents/v002_c_throttle.py"),
        ("v003", "agents/v003_dynamic_labor.py")
    ]
    
    print("=== SMOKE BENCHMARK ===")
    smoke_tasks = []
    for var_name, var_path in variants:
        for seed in range(1, 6):
            smoke_tasks.append((var_name, var_path, "random", "random", seed))
            
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        smoke_results = pool.map(run_match, smoke_tasks)
        
    v002_smoke = [r["p1_money"] for r in smoke_results if r["variant"] == "v002_c"]
    v003_smoke = [r["p1_money"] for r in smoke_results if r["variant"] == "v003"]
    
    v002_mean = sum(v002_smoke) / len(v002_smoke)
    v003_mean = sum(v003_smoke) / len(v003_smoke)
    
    print(f"Smoke Test Results (5 games vs random):")
    print(f"V002 Mean: ${v002_mean:.2f}")
    print(f"V003 Mean: ${v003_mean:.2f}")
    
    # We proceed even if V003 is lower in the smoke test to get full data, 
    # but we print a warning.
    if v003_mean < v002_mean:
        print("WARNING: V003 performed worse than V002 in smoke test.")
        
    print("\n=== FULL BENCHMARK (180 games) ===")
    opponents = [
        ("random", "random"),
        ("starter", "starter"),
        ("melon_maxxer", "agents/melon_maxxer.py")
    ]
    
    full_tasks = []
    for var_name, var_path in variants:
        for opp_name, opp_path in opponents:
            for seed in range(101, 131): # 30 seeds
                full_tasks.append((var_name, var_path, opp_name, opp_path, seed))
                
    start_time = time.time()
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        full_results = pool.map(run_match, full_tasks)
        
    print(f"Completed in {time.time() - start_time:.2f} seconds.")
    
    with open("experiments/v003_benchmark_results.json", "w") as f:
        json.dump(full_results, f, indent=2)
        
    print("Results saved to experiments/v003_benchmark_results.json")
