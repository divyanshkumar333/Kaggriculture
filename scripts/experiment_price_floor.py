from kaggle_environments.envs.kaggriculture.kaggriculture import (
    market_price, MARKET_PARAMS, _commit_unit, _refresh_prices, _new_market, _new_farm, _new_private
)

def run_experiment():
    market = _new_market()
    farm = _new_farm(10, 3000)
    private = _new_private()
    
    # Give the farm 2000 MELON in the shed
    private["shed"]["MELON"] = 2000
    
    print(f"Initial Market Inventory: {market['inventory']['MELON']}")
    print(f"Initial Price: {market['prices']['MELON']}")
    
    # Sell 2000 MELON unit by unit
    revenue = 0
    for i in range(2000):
        price = market_price("MELON", market["inventory"]["MELON"])
        ok = _commit_unit("SELL", "MELON", price, farm, private, market, 10000)
        if ok:
            revenue += price
            
    print(f"After Selling 2000 MELON:")
    print(f"Market Inventory: {market['inventory']['MELON']}")
    print(f"Price: {market_price('MELON', market['inventory']['MELON'])}")
    print(f"Total Revenue: {revenue}")
    
    # Town consumes 1 MELON
    market['inventory']['MELON'] -= 1
    _refresh_prices(market)
    
    print(f"After Town Consumes 1 MELON:")
    print(f"Market Inventory: {market['inventory']['MELON']}")
    print(f"Price: {market['prices']['MELON']}")

if __name__ == "__main__":
    run_experiment()
