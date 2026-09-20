from kaggle_environments import make
import importlib.util, sys
import os
if os.path.exists('crash.txt'): os.remove('crash.txt')
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('v', 'scripts/v100test2.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', configuration={'episodeSteps': 97, 'randomSeed': 8100}, debug=False)
env.run([mod.agent, 'pass'])
