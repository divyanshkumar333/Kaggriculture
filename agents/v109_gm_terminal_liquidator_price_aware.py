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
        
        # Keep BUY_PRODUCT and HIRE
        for o in market_orders:
            if not isinstance(o, list): o = list(o)
            if len(o) > 0 and o[0] in ('BUY_PRODUCT', 'HIRE'):
                new_market.append(o)
        
        shed = obs['private']['shed']
        market_prices = obs.get("market", {}).get("prices", {})
        
        base_prices = {"MELON": 250, "STRAWBERRY": 120, "MILK": 160, "WOOL": 150, "EGG": 50, "CARROT": 35, "TOMATO": 60, "WHEAT": 25, "FERTILIZER": 10}
        
        shed_total = sum(shed.values())
        
        sell_candidates = []
        for prod, count in shed.items():
            if count <= 0: continue
            
            price = market_prices.get(prod, 0)
            base = base_prices.get(prod, 50)
            
            if day == 29:
                # Dump everything on last day
                sell_candidates.append((price, prod, count))
                continue
                
            batch = 0
            # Dynamic pricing tiers
            if price >= base * 0.9:
                batch = 6
            elif price >= base * 0.7:
                batch = 3
            elif price >= base * 0.4:
                batch = 1
                
            if batch > 0:
                sell_candidates.append((price, prod, min(count, batch)))
            elif shed_total > 85 and prod in ('FERTILIZER', 'WHEAT', 'CARROT'):
                # Shed overflow protection: trickle cheap items
                sell_candidates.append((price, prod, min(count, 2)))
                
        # Sort by highest price to prioritize limited 10 market slots
        sell_candidates.sort(reverse=True)
        
        for price, prod, count in sell_candidates:
            if len(new_market) >= 10: break
            new_market.append(["SELL", prod, count])
            
        action['market'] = new_market[:10]
        
    return action
