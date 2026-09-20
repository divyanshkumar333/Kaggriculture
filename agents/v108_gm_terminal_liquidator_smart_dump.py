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
        
        # Keep BUY_PRODUCT and HIRE. Strip BUY_SEED, BUY_ANIMAL, SELL
        for o in market_orders:
            if not isinstance(o, list): o = list(o)
            if len(o) > 0 and o[0] in ('BUY_PRODUCT', 'HIRE'):
                new_market.append(o)
        
        shed = obs['private']['shed']
        market_prices = obs.get("market", {}).get("prices", {})
        
        sell_candidates = []
        # Dump all premium items immediately, never hold.
        # But keep WHEAT for feeding animals. FERTILIZER is not very valuable, so we skip it to save order slots.
        for prod, count in shed.items():
            if count > 0 and prod not in ('WHEAT', 'FERTILIZER'):
                sell_candidates.append( (market_prices.get(prod, 0), prod, count) )
        
        # If it's the very last hours of the game, dump everything including WHEAT and FERTILIZER
        if day == 29 and obs['hour'] >= 20:
            for prod in ('WHEAT', 'FERTILIZER'):
                if shed.get(prod, 0) > 0:
                    sell_candidates.append( (market_prices.get(prod, 0), prod, shed[prod]) )
        
        sell_candidates.sort(reverse=True)
        
        for price, prod, count in sell_candidates:
            if len(new_market) >= 10: break
            new_market.append(["SELL", prod, count])
                        
        action['market'] = new_market[:10]
        
    return action
