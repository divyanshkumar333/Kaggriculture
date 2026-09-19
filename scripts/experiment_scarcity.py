from kaggle_environments.envs.kaggriculture.kaggriculture import (
    market_price, _commit_unit, _new_market, _new_farm, _new_private
)

def run_experiment():
    market = _new_market()
    farm = _new_farm(10, 3000)
    private = _new_private()
    
    for product in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]:
        market = _new_market()
        farm = _new_farm(10, 3000)
        private = _new_private()
        
        # Simulate town consuming 500 units over the game
        market['inventory'][product] -= 500
        
        private["shed"][product] = 50
        
        revenue = 0
        for i in range(50):
            price = market_price(product, market["inventory"][product])
            ok = _commit_unit("SELL", product, price, farm, private, market, 10000)
            if ok:
                revenue += price
                
        print(f"{product:12} | Inv: {market['inventory'][product]} | Final Price: {market_price(product, market['inventory'][product])} | Total Revenue (50): {revenue}")

if __name__ == "__main__":
    run_experiment()
