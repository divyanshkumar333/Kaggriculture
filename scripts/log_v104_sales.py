from kaggle_environments import make

def log_v104_sales():
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run(["submission_v104_quote_priority.py", "pass"])
    
    total_sales = {"MELON": 0, "STRAWBERRY": 0, "MILK": 0, "WOOL": 0, "WHEAT": 0, "CARROT": 0}
    total_cash_from_sales = {"MELON": 0, "STRAWBERRY": 0, "MILK": 0, "WOOL": 0, "WHEAT": 0, "CARROT": 0}
    
    # We can inspect the market prices and the player's money at each step
    prev_money = 3000
    for step in env.steps[1:]:
        obs = step[0].observation
        me = obs["farms"][0]
        money = me["money"]
        market_orders = step[0].action.get("market", []) if step[0].action else []
        
        # This is a bit tricky since the market executes simultaneously and we don't 
        # get the exact matched prices easily in the observation.
        # But we can look at the delta in money.
        diff = money - prev_money
        prev_money = money
        
        for order in market_orders:
            if len(order) >= 3 and order[0] == "SELL":
                prod = order[1]
                qty = int(order[2])
                if prod in total_sales:
                    total_sales[prod] += qty
                    
    print(f"V104 Total Attempted Sales: {total_sales}")
    print(f"Final Money: {prev_money}")

if __name__ == "__main__":
    log_v104_sales()
