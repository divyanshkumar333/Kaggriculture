from kaggle_environments import make

def test_market_math():
    env = make("kaggriculture", configuration={"episodeSteps": 10}, debug=True)
    
    # We will write two custom agents.
    # Agent 1 will buy 14 wheat.
    # Agent 2 will buy 34 wheat.
    
    def agent1(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 14]]}
        if obs["step"] == 1:
            return {"farmer": ["PASS"], "market": [["SELL", "WHEAT", 9]]}
        return {"farmer": ["PASS"], "market": []}
        
    def agent2(obs):
        if obs["step"] == 0:
            return {"farmer": ["PASS"], "market": [["BUY_PRODUCT", "WHEAT", 34]]}
        return {"farmer": ["PASS"], "market": []}
        
    print("Testing Risk-Free Exploit vs Heavy Buyer (v057-style)")
    env.run([agent1, agent2])
    
    for i, step in enumerate(env.steps):
        obs = step[0].observation
        if "market" in obs:
            price = obs["market"]["prices"].get("WHEAT", 10)
            inv = obs["market"]["inventory"].get("WHEAT", 10000)
            p1_money = obs["farms"][0]["money"]
            p2_money = obs["farms"][1]["money"]
            print(f"Step {i} | Wheat Price: {price} | Inv: {inv} | P1 Money: {p1_money} | P2 Money: {p2_money}")

if __name__ == "__main__":
    test_market_math()
