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
        # Stop buying seeds and animals. Continue buying products (wheat for feed)
        market_orders = action.get('market', [])
        filtered_orders = []
        for o in market_orders:
            if not isinstance(o, list):
                o = list(o)
            if len(o) > 0 and o[0] not in ('BUY_SEED', 'BUY_ANIMAL'):
                filtered_orders.append(o)
        
        action['market'] = filtered_orders[:10]
        
    return action
