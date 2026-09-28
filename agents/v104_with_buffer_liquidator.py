import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
v104_path = os.path.join(os.path.dirname(__file__), 'v104_quote_priority.py')
spec = importlib.util.spec_from_file_location('m', v104_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    action = mod.agent(obs, cfg)
    if not isinstance(action, dict): return action
    
    player = obs['player']
    farm = obs['farms'][player]
    priv = obs['private']
    step = int(obs['step'])
    day = step // 24
    
    if day >= 25: return action
    
    money = farm['money']
    prices = obs['market']['prices']
    market_orders = action.get('market', [])
    
    # Calculate projected money after base agent's market orders
    projected_money = money
    for o in market_orders:
        if o and o[0] == 'SELL':
            item = o[1]
            amt = int(o[2])
            projected_money += amt * prices.get(item, 1)
        elif o and o[0] == 'BUY_SEED':
            item = o[1]
            amt = int(o[2])
            # Seed prices are fixed, roughly
            seed_prices = {'WHEAT':10, 'CARROT':20, 'TOMATO':50, 'STRAWBERRY':100, 'MELON':80}
            projected_money -= amt * seed_prices.get(item, 10)
        elif o and o[0] == 'HIRE':
            # Not easy to know the exact cost here without counting, but we can assume -50
            projected_money -= 50
            
    # We want at least 4000 buffer to allow scaling
    target_buffer = 4000
    
    if projected_money < target_buffer and len(farm.get('hands', [])) < 10:
        shed = priv.get('shed', {})
        
        # Calculate how much of each crop we have left AFTER base agent's sells
        left_in_shed = dict(shed)
        for o in market_orders:
            if o and o[0] == 'SELL':
                left_in_shed[o[1]] = max(0, left_in_shed.get(o[1], 0) - int(o[2]))
        
        # Critical assets: We need WHEAT to feed animals.
        animal_count = sum(1 for row in farm['tiles'] for t in row if isinstance(t, dict) and t.get('kind') in ('COOP', 'PASTURE') and 'animal' in t)
        wheat_needed = animal_count * 2 # 2 days buffer
        
        sellable = []
        for item in ['CARROT', 'TOMATO', 'MELON', 'STRAWBERRY', 'WHEAT']:
            amt = left_in_shed.get(item, 0)
            if item == 'WHEAT':
                amt = max(0, amt - wheat_needed)
            if amt > 0:
                sellable.append(item)
                
        # Sort by lowest price first to preserve high-value crops if possible
        sellable.sort(key=lambda x: prices.get(x, 1))
        
        shortfall = target_buffer - projected_money
        new_orders = []
        
        for item in sellable:
            if shortfall <= 0 or len(market_orders) + len(new_orders) >= 10:
                break
            amt_to_sell = left_in_shed[item]
            # Don't sell more than we need
            needed_amt = int(shortfall // prices.get(item, 1)) + 1
            amt_to_sell = min(amt_to_sell, needed_amt)
            
            if amt_to_sell > 0:
                new_orders.append(['SELL', item, amt_to_sell])
                shortfall -= amt_to_sell * prices.get(item, 1)
                
        if new_orders:
            action['market'] = market_orders + new_orders
            
    return action
