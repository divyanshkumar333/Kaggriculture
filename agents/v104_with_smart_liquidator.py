import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
v104_path = os.path.join(os.path.dirname(__file__), 'v104_quote_priority.py')
spec = importlib.util.spec_from_file_location('m', v104_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    # If we are stuck in early/mid game with low cash and low hands, sell crops to reach the buffer.
    # We do this BEFORE the base agent runs, by modifying the obs, or we do it AFTER by injecting SELLs at the start.
    # Actually, injecting SELLs at the start of the base agent's market orders is safest.
    
    player = obs['player']
    step = int(obs['step'])
    day = step // 24
    
    # Run the base agent
    action = mod.agent(obs, cfg)
    
    if not isinstance(action, dict):
        return action
        
    if day >= 25:
        return action
        
    farm = obs['farms'][player]
    priv = obs['private']
    money = farm['money']
    current_hands = len(farm.get('hands', [])) + 1
    
    # If we have less than 10 hands, and less than 3500 cash, we are bottlenecked by the buffer.
    if current_hands < 10 and money < 3500:
        shed = priv.get('shed', {})
        prices = obs['market']['prices']
        sellable = [item for item in ['WHEAT', 'CARROT', 'TOMATO', 'MELON', 'STRAWBERRY'] if shed.get(item, 0) > 0]
        
        # Sort by least damaging (lowest price first)
        sellable.sort(key=lambda x: prices.get(x, 1))
        
        shortfall = 3500 - money
        new_orders = []
        
        for item in sellable:
            if shortfall <= 0 or len(new_orders) >= 3: # max 3 sell orders to avoid taking all slots
                break
            amount_to_sell = min(shed[item], (shortfall // prices.get(item, 1)) + 1)
            if amount_to_sell > 0:
                new_orders.append(['SELL', item, amount_to_sell])
                shortfall -= amount_to_sell * prices.get(item, 1)
        
        if new_orders:
            market_orders = action.get('market', [])
            # Prepend the new sell orders so they execute first
            action['market'] = (new_orders + market_orders)[:10]
            
    return action
