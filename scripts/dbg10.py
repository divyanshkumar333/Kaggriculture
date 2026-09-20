from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'agents/v100b_gm_fixed_opening.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)

f = open('hires_log.txt', 'w')
def agent(obs, cfg):
    a = mod.agent(obs)
    if obs['day'] in (1, 2) and obs['hour'] == 0:
        me = obs['farms'][0]
        f.write(f"Day {obs['day']} Hour 0: hires_today={me.get('hires_today', 'MISSING')}\n")
    return a

env.run([agent, 'pass'])
f.close()
