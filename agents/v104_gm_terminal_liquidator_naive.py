import sys, os, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    action = mod.agent(obs, cfg)
    day = obs['day']
    
    if day >= 25:
        market_orders = action.get('market', [])
        new_market = []
        
        # Keep BUY and HIRE
        for o in market_orders:
            if not isinstance(o, list): o = list(o)
            if len(o) > 0 and o[0] != 'SELL':
                new_market.append(o)
        
        # Naive Dump: sell EVERYTHING immediately
        shed = obs['private']['shed']
        
        # We can submit up to 10 orders per turn.
        # We sort by current price to ensure we sell the most valuable stuff first if > 10 items.
        market_prices = obs.get("market", {}).get("prices", {})
        sell_candidates = []
        for prod, count in shed.items():
            if count > 0:
                sell_candidates.append( (market_prices.get(prod, 0), prod, count) )
        
        sell_candidates.sort(reverse=True)
        
        for price, prod, count in sell_candidates:
            if len(new_market) >= 10: break
            new_market.append(["SELL", prod, count])
            
        action['market'] = new_market[:10]
        
    return action
