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
        
        shed_total = sum(shed.values())
        
        sell_candidates = []
        for prod, count in shed.items():
            if count > 0:
                sell_candidates.append( (market_prices.get(prod, 0), prod, count) )
        
        # Sort by price. If day == 29, sell most expensive first. If day < 29, sell cheapest first to free space.
        if day == 29:
            sell_candidates.sort(reverse=True)
            for price, prod, count in sell_candidates:
                if len(new_market) >= 10: break
                new_market.append(["SELL", prod, count])
        else:
            if shed_total > 80:
                sell_candidates.sort(reverse=False)  # cheapest first
                # Sell enough to get back down to 50
                to_sell = shed_total - 50
                for price, prod, count in sell_candidates:
                    if len(new_market) >= 10: break
                    sell_amt = min(count, to_sell)
                    if sell_amt > 0:
                        new_market.append(["SELL", prod, sell_amt])
                        to_sell -= sell_amt
                    if to_sell <= 0:
                        break
                        
        action['market'] = new_market[:10]
        
    return action
