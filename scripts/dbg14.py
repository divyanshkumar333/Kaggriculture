from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'agents/v100b_gm_fixed_opening.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)

def agent(obs, cfg):
    a = mod.agent(obs)
    if obs['day'] in (1, 2) and obs['hour'] == 0:
        me = obs['farms'][0]
        print(f"Day {obs['day']} Hour 0: money={me['money']} hires={me.get('hires_today')} market={a.get('market')}")
    if obs['day'] in (1, 2) and obs['hour'] == 1:
        me = obs['farms'][0]
        print(f"Day {obs['day']} Hour 1: hands={len(me.get('hands', []))}")
    return a

env.run([agent, 'pass'])
