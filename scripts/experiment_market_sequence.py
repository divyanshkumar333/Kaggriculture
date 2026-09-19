from kaggle_environments import make

def run_experiment():
    print("=== EXPERIMENT 1: Does market action order matter? ===")
    
    # We will BUY 50 wheat on step 0, then SELL 20 wheat on step 1.
    
    def agent_p0(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 20]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 10], ["SELL", "WHEAT", 10]]}
        return {"farmer": ["PASS"], "market": []}
        
    def agent_p1(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 20]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 20]]}
        return {"farmer": ["PASS"], "market": []}
        
    env = make("kaggriculture", configuration={"episodeSteps": 3}, debug=True)
    env.run([agent_p0, agent_p1])
    
    p0_revenue = env.steps[2][0].observation['farms'][0]['money'] - env.steps[1][0].observation['farms'][0]['money']
    p1_revenue = env.steps[2][0].observation['farms'][1]['money'] - env.steps[1][0].observation['farms'][1]['money']
    
    print(f"P0 Revenue from 2x 10 WHEAT: {p0_revenue}")
    print(f"P1 Revenue from 1x 20 WHEAT: {p1_revenue}")
    
    print("\n=== EXPERIMENT 2: P0 vs P1 ordering ===")
    def agent_p0_single(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 10]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 10]]}
        return {"farmer": ["PASS"], "market": []}
        
    def agent_p1_single(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 10]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 10]]}
        return {"farmer": ["PASS"], "market": []}
        
    env = make("kaggriculture", configuration={"episodeSteps": 3}, debug=True)
    env.run([agent_p0_single, agent_p1_single])
    
    p0_revenue = env.steps[2][0].observation['farms'][0]['money'] - env.steps[1][0].observation['farms'][0]['money']
    p1_revenue = env.steps[2][0].observation['farms'][1]['money'] - env.steps[1][0].observation['farms'][1]['money']
    
    print(f"P0 Revenue from 1x 10 WHEAT: {p0_revenue}")
    print(f"P1 Revenue from 1x 10 WHEAT: {p1_revenue}")
    
    print("\n=== EXPERIMENT 3: Does breaking up orders change revenue? ===")
    def agent_p0_split(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 10]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 1] for _ in range(10)]}
        return {"farmer": ["PASS"], "market": []}
        
    env = make("kaggriculture", configuration={"episodeSteps": 3}, debug=True)
    env.run([agent_p0_split, agent_p1_single])
    
    p0_revenue = env.steps[2][0].observation['farms'][0]['money'] - env.steps[1][0].observation['farms'][0]['money']
    p1_revenue = env.steps[2][0].observation['farms'][1]['money'] - env.steps[1][0].observation['farms'][1]['money']
    
    print(f"P0 Revenue from 10x 1 WHEAT: {p0_revenue}")
    print(f"P1 Revenue from 1x 10 WHEAT: {p1_revenue}")

if __name__ == "__main__":
    run_experiment()
