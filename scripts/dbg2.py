from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'agents/v100b_gm_fixed_opening.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)

def agent(obs, cfg):
    me = obs['farms'][0]
    priv = obs['private']
    shed = priv['shed']
    tiles = me['tiles']
    if obs['day'] <= 4 and obs['hour'] == 0:
        animals = []
        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if isinstance(t, dict) and t.get('kind') in ('COOP','PASTURE'):
                    animals.append((c,r,t.get('animal'),t.get('fed_today'),t.get('consecutive_unfed')))
        wh = shed.get('WHEAT', 0)
        inv_wh = sum(i.get('WHEAT',0) for i in priv['inventories'] if isinstance(i,dict))
        print('Day', obs['day'], 'money=', me['money'], 'wheat=', wh+inv_wh, 'animals=', len(animals), animals[:4])
    return mod.agent(obs)

env.run([agent, 'random'])
final = env.steps[-1]
print('Final P0:', final[0].reward)
