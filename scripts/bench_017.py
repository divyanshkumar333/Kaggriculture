from kaggle_environments import make

def run_experiment():
    print("=== BENCHMARK: 017_melon_tomato vs 014_robust_trace ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/017_melon_tomato.py", "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (017 Hybrid) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Base) Money: {obs['farms'][1]['money']}")
    
    print(f"P0 TOMATO in shed: {obs['private']['shed'].get('TOMATO', 0)}")
    print(f"Final TOMATO Price: {obs['market']['prices']['TOMATO']}")
    print(f"Final TOMATO Inventory: {obs['market']['inventory']['TOMATO']}")

if __name__ == "__main__":
    run_experiment()
