from kaggle_environments import make
env = make('kaggriculture', configuration={'episodeSteps': 3, 'randomSeed': 42}, debug=False)
steps = env.run(['pass', 'pass'])
obs = steps[0][0].observation
print('Market prices (seed 42, step 0):')
import json
print(json.dumps(obs.get('market', {}), indent=2))
