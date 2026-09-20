from kaggle_environments import make
import json
env = make('kaggriculture', configuration={'episodeSteps': 3, 'randomSeed': 42}, debug=False)
steps = env.run(['pass', 'pass'])
obs = steps[0][0].observation
# Print configuration
cfg = env.configuration
print('Config:', json.dumps(dict(cfg), indent=2))
