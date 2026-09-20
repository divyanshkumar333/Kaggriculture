import sys, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    action = mod.agent(obs, cfg)
    day = obs['day']
    
    if day >= 25:
        # 1. Stop buying things that won't mature
        market = []
        for order in action.get('market', []):
            if order[0] not in ('BUY_SEED', 'BUY_ANIMAL', 'BUY_LAND'):
                market.append(order)
        action['market'] = market
        
        # 2. Stop feeding and caring for animals (saves WHEAT for selling)
        # Stop planting crops (waste of time, seed already bought, but whatever)
        def process_unit(unit_action):
            if unit_action and unit_action[0] in ('FEED', 'CARE', 'PLANT'):
                return ['PASS']
            return unit_action
            
        action['farmer'] = process_unit(action.get('farmer', ['PASS']))
        action['hands'] = [process_unit(h) for h in action.get('hands', [])]
        
        # 3. Liquidate WHEAT (since trace probably planned to feed it, not sell it)
        private = obs.get('private', {})
        shed = private.get('shed', {})
        wheat_qty = shed.get('WHEAT', 0)
        if wheat_qty > 0:
            # Check if we are already selling wheat
            selling = False
            for m in action['market']:
                if m[0] == 'SELL' and m[1] == 'WHEAT':
                    m[2] += wheat_qty
                    selling = True
                    break
            if not selling and len(action['market']) < 10:
                action['market'].append(['SELL', 'WHEAT', wheat_qty])
                
        # Also liquidate FERTILIZER just in case
        fert_qty = shed.get('FERTILIZER', 0)
        if fert_qty > 0:
            selling = False
            for m in action['market']:
                if m[0] == 'SELL' and m[1] == 'FERTILIZER':
                    m[2] += fert_qty
                    selling = True
                    break
            if not selling and len(action['market']) < 10:
                action['market'].append(['SELL', 'FERTILIZER', fert_qty])

    return action
