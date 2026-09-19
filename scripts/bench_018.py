from kaggle_environments import make

def run_experiment():
    print("=== BENCHMARK: 018_contrarian_swarm vs 014_robust_trace ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/018_contrarian_swarm.py", "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (018 Contrarian) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Base) Money: {obs['farms'][1]['money']}")
    
    hands = len(obs['farms'][0]['hands'])
    print(f"P0 Hands at end: {hands}")
    print(f"Unlocked quadrants: {obs['farms'][0]['unlocked_quadrants']}")
    
    for item in ["CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "WHEAT"]:
        print(f"{item}: Price={obs['market']['prices'][item]}, Inv={obs['market']['inventory'][item]}")

if __name__ == "__main__":
    run_experiment()
