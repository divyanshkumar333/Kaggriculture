
from kaggle_environments import make
import importlib.util

def load_agent(path):
    spec = importlib.util.spec_from_file_location('agent_module', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v057 = load_agent('agents/v057_demand_residual.py')
kaito = load_agent('RESEARCH/external/kaito_v27_real/main.py')

env = make('kaggriculture', debug=True)
env.run([v057, kaito])
final = env.steps[-1]
print('V057 Reward:', final[0].reward)
print('Kaito Reward:', final[1].reward)
