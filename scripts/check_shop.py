from kaggle_environments import make
import json

# Check actual animal and seed buy costs by running an agent that does the buy and checks money
env = make('kaggriculture', configuration={'episodeSteps': 3, 'randomSeed': 42}, debug=False)

def test_buys(obs, cfg):
    if obs.get('step', 0) == 0:
        return {'farmer': ['PASS'], 'hands': [], 'market': [
            ['BUY_ANIMAL', 'SHEEP', 1],
            ['BUY_ANIMAL', 'COW', 1],
            ['BUY_SEED', 'MELON', 1],
            ['BUY_SEED', 'WHEAT', 1],
            ['BUY_SEED', 'STRAWBERRY', 1],
        ]}
    return {'farmer': ['PASS'], 'hands': [], 'market': []}

steps = env.run([test_buys, 'pass'])
step0_money = steps[0][0].observation['farms'][0]['money']
step1_money = steps[1][0].observation['farms'][0]['money']
step1_seeds = steps[1][0].observation['private']['seeds']
step1_shed = steps[1][0].observation['private']['shed']
print('Step 0 money:', step0_money)
print('Step 1 money:', step1_money)
print('Money spent:', step0_money - step1_money)
print('Seeds:', step1_seeds)
print('Shed:', step1_shed)
