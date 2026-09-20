from kaggle_environments import make
import importlib.util, sys
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'agents/v100b_gm_fixed_opening.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

old_agent = mod.agent
def my_agent(obs):
    if obs['day'] == 2 and obs['hour'] == 0:
        money = obs['farms'][0]['money']
        hires = obs['farms'][0].get('hires_today', 0)
        print(f"BEFORE AGENT: day 2 hour 0 money={money} hires={hires}")
    a = old_agent(obs)
    if obs['day'] == 2 and obs['hour'] == 0:
        print(f"AFTER AGENT: market={a.get('market')}")
    return a

mod.agent = my_agent

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)
env.run([mod.agent, 'pass'])
