from kaggle_environments import make
import importlib.util, sys

env = make('kaggriculture', configuration={'episodeSteps': 720, 'randomSeed': 9000}, debug=False)
steps = env.run(['main.py', 'main.py'])
last_obs = steps[-1][0].observation
print("Player 0 Money:", last_obs['farms'][0]['money'])
print("Player 0 Shed:", last_obs['private']['shed'])
print("Player 0 Seeds:", last_obs['private']['seeds'])
