import json
import sys
from kaggle_environments import make

def main():
    # Run a short game to generate a replay
    print('Running game...')
    env = make('kaggriculture', configuration={'episodeSteps': 10, 'randomSeed': 42}, debug=False)
    env.run(['random', 'random'])
    replay = env.toJSON()
    
    steps = replay['steps']
    print(f'Original game ran for {len(steps)} steps.')
    
    # Try to initialize a new env at step 5
    print('Initializing new env from step 5...')
    env2 = make('kaggriculture', configuration={'episodeSteps': 10, 'randomSeed': 42}, steps=steps[:5], debug=False)
    print(f'New env initialized. len(env2.steps) = {len(env2.steps)}')
    print(f'Current step index in new env: {env2.state[0].observation.step}')
    
    print('Running from step 5...')
    env2.run(['random', 'random'])
    print(f'New game ran for {len(env2.steps)} steps.')

if __name__ == '__main__':
    main()
