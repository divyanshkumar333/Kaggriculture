from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'agents/v100b_gm_fixed_opening.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)

def agent(obs, cfg):
    if obs['day'] in (1, 2) and obs['hour'] in (0, 1):
        me = obs['farms'][0]
        print(f"Day {obs['day']} Hour {obs['hour']}: money={me['money']} hands={len(me.get('hands',[]))}")
    return mod.agent(obs)

env.run([agent, 'random'])
