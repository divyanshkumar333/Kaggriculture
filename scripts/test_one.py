import sys
import json
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": 1337}, debug=True)
steps = env.run([sys.argv[1], sys.argv[2]])
print("Agent 1 Status:", steps[-1][0]['status'], "Reward:", steps[-1][0]['reward'])
print("Agent 2 Status:", steps[-1][1]['status'], "Reward:", steps[-1][1]['reward'])
