from kaggle_environments import make

def run_experiment():
    print("=== BENCHMARK: 016_dynamic_parasite vs 014_robust_trace ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/016_dynamic_parasite.py", "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (016 Dynamic) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Base) Money: {obs['farms'][1]['money']}")
    
    # Let's see how many swarm hands they hired
    hands = len(obs['farms'][0]['hands'])
    print(f"P0 Hands at end: {hands}")
    print(f"Unlocked quadrants: {obs['farms'][0]['unlocked_quadrants']}")
    
    # What was the chosen crop?
    # We can infer it from the inventory or final prices
    for item in ["CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "WHEAT"]:
        print(f"{item}: Price={obs['market']['prices'][item]}, Inv={obs['market']['inventory'][item]}")

if __name__ == "__main__":
    run_experiment()
