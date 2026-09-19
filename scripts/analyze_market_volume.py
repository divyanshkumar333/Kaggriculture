from kaggle_environments import make

def run_experiment():
    print("=== MARKET VOLUME ANALYSIS ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/014_robust_trace.py", "agents/014_robust_trace.py"])
    
    # We want to trace how many of each item were sold by both players.
    sales = {0: {}, 1: {}}
    
    for step_idx, step in enumerate(env.steps):
        if step_idx == 0: continue
        for p in [0, 1]:
            action = step[p].action
            if action and "market" in action:
                for order in action["market"]:
                    if len(order) >= 3 and order[0] == "SELL":
                        item = order[1]
                        qty = int(order[2])
                        sales[p][item] = sales[p].get(item, 0) + qty
                        
    final_obs = env.steps[-1][0].observation
    market_inv = final_obs["market"]["inventory"]
    prices = final_obs["market"]["prices"]
    
    print("Sales by P0:", sales[0])
    print("Sales by P1:", sales[1])
    print("Final Market Inventory:", market_inv)
    print("Final Prices:", prices)
    print(f"P0 Money: {final_obs['farms'][0]['money']}")
    print(f"P1 Money: {final_obs['farms'][1]['money']}")

if __name__ == "__main__":
    run_experiment()
