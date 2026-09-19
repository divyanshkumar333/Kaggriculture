from kaggle_environments import make

def run_experiment():
    print("=== EXPERIMENT: TOMATO SPECULATOR vs 014_robust_trace ===")
    
    def agent_speculator(obs):
        step = obs["step"]
        private = obs["private"]
        
        market = []
        
        # Day 1 (turn 24): Buy 50 TOMATOES
        # Wait, if we buy 50 at once, the price goes up.
        # But we only need a simple order.
        if step == 24:
            market.append(["BUY_PRODUCT", "TOMATO", 50])
            
        # Turn 718: Sell 50 TOMATOES
        if step == 718:
            tomatoes = private["shed"].get("TOMATO", 0)
            if tomatoes > 0:
                market.append(["SELL", "TOMATO", tomatoes])
                
        return {"farmer": ["PASS"], "market": market}
        
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run([agent_speculator, "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (Speculator) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Robust Trace) Money: {obs['farms'][1]['money']}")
    print(f"Final TOMATO Price: {obs['market']['prices']['TOMATO']}")
    print(f"Final TOMATO Inventory: {obs['market']['inventory']['TOMATO']}")

if __name__ == "__main__":
    run_experiment()
