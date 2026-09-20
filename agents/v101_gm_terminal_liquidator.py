import sys, os, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    # Call the champion agent
    action = mod.agent(obs, cfg)
    
    # Terminal liquidation on Day 25+
    day = obs['day']
    if day >= 25:
        # Ignore current trace market orders for buying, keep only HIRE and SELL.
        # This stops capital investment while using main.py's optimized selling.
        market_orders = action.get('market', [])
        filtered_orders = []
        for o in market_orders:
            if not isinstance(o, list):
                o = list(o)
            if len(o) > 0 and o[0] in ('SELL', 'HIRE'):
                filtered_orders.append(o)
        
        action['market'] = filtered_orders[:10]
        
    return action
