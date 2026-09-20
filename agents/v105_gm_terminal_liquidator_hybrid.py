import sys, os, importlib.util
sys.path.insert(0, '.')

spec_main = importlib.util.spec_from_file_location('m_main', 'main.py')
mod_main = importlib.util.module_from_spec(spec_main)
spec_main.loader.exec_module(mod_main)

spec_algo = importlib.util.spec_from_file_location('m_algo', 'agents/v100b_gm_fixed_opening.py')
mod_algo = importlib.util.module_from_spec(spec_algo)
spec_algo.loader.exec_module(mod_algo)

def agent(obs, cfg=None):
    day = obs['day']
    if day >= 25:
        # Ignore current trace and switch to algorithmic bot for terminal liquidation
        return mod_algo.agent(obs)
    else:
        # Use champion trace for early/mid game
        return mod_main.agent(obs, cfg)
