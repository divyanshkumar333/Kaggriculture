from kaggle_environments import make
import json

def run_experiment():
    print("=== BENCHMARK: 015_tomato_parasite vs 014_robust_trace ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/015_tomato_parasite.py", "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (015 Parasite) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Robust Trace) Money: {obs['farms'][1]['money']}")
    print(f"Final TOMATO Price: {obs['market']['prices']['TOMATO']}")
    print(f"Final TOMATO Inventory: {obs['market']['inventory']['TOMATO']}")
    print(f"P0 TOMATO in shed: {obs['private']['shed'].get('TOMATO', 0)}")
    
if __name__ == "__main__":
    run_experiment()
