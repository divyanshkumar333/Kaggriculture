import sys, os, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    # Bypass front_run and repay entirely on day 25+ by monkeypatching the state?
    # Actually, we can just let mod.agent run, then filter the market orders.
    # mod.agent will apply _front_run and _repay, but we will strip all SELLs!
    
    action = mod.agent(obs, cfg)
    day = obs['day']
    
    if day >= 25:
        market_orders = action.get('market', [])
        new_market = []
        # Keep only BUY and HIRE orders from the trace
        for o in market_orders:
            if not isinstance(o, list):
                o = list(o)
            if len(o) > 0 and o[0] != 'SELL':
                new_market.append(o)
        
        # Add our own paced SELL logic
        shed = obs['private']['shed']
        market_prices = obs.get("market", {}).get("prices", {})
        
        for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(new_market) >= 10: break
            p_count = shed.get(prod, 0)
            if p_count <= 0: continue
            cur_price = market_prices.get(prod, 100)
            
            # Pacing logic: sell more aggressively as the game ends
            if day >= 28:
                batch = 20  # Sell everything
            elif day == 27:
                batch = 12
            elif cur_price >= 80:
                batch = 8
            else:
                batch = 4
                
            new_market.append(["SELL", prod, min(p_count, batch)])
            
        action['market'] = new_market[:10]
        
    return action
