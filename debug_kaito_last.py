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

def wrapped_kaito(obs, cfg):
    action = kaito(obs, cfg)
    if obs['step'] >= 718:
        print(f'Step {obs["step"]} Kaito Market: {action.get("market")}')
    return action

env.run([v057, wrapped_kaito])
