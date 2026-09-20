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
        
        player = obs['player']
        animal_count = 0
        for r in range(len(obs['farms'][player]['tiles'])):
            for c in range(len(obs['farms'][player]['tiles'][r])):
                tile = obs['farms'][player]['tiles'][r][c]
                if isinstance(tile, dict) and tile.get('kind') in ('COOP', 'PASTURE') and 'animal' in tile:
                    animal_count += 1
                    
        wheat_to_keep = animal_count * 2 # Need enough to feed
        
        shed = obs['private']['shed']
        market_prices = obs.get("market", {}).get("prices", {})
        
        sell_candidates = []
        for prod, count in shed.items():
            if count <= 0: continue
            
            sell_amt = count
            if prod == 'WHEAT':
                sell_amt = max(0, count - wheat_to_keep)
                
            if sell_amt > 0:
                price = market_prices.get(prod, 0)
                sell_candidates.append((price, prod, sell_amt))
                
        # Sort by highest price to prioritize limited 10 market slots
        sell_candidates.sort(reverse=True)
        
        for price, prod, count in sell_candidates:
            if len(new_market) >= 10: break
            new_market.append(["SELL", prod, count])
            
        action['market'] = new_market[:10]
        
    return action
