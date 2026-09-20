from kaggle_environments import make
import importlib.util, sys
import os
if os.path.exists('debug_market.txt'): os.remove('debug_market.txt')
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'scripts/v100test.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)
env.run([mod.agent, 'pass'])
