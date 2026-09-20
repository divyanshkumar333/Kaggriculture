import sys, os, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    if 'agent_state' not in obs['private']:
        obs['private']['agent_state'] = {}
        
    state = obs['private']['agent_state']
    day = obs['day']
    
    if day >= 25:
        state['lookahead'] = 0  # Disable front running
    else:
        state['lookahead'] = 4
        
    return mod.agent(obs, cfg)
