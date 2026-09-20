from kaggle_environments import make
import importlib.util, sys

env = make('kaggriculture', configuration={'episodeSteps': 720, 'randomSeed': 9000}, debug=False)
steps = env.run(['main.py', 'main.py'])
# trace the buying actions of player 0 in the last 10 days
for step, (p0, p1) in enumerate(steps):
    day = step // 24
    if day >= 20:
        if p0.action and 'market' in p0.action:
            for o in p0.action['market']:
                if o[0] in ('BUY_SEED', 'BUY_ANIMAL'):
                    print(f"Day {day} Step {step} bought {o[1]} x {o[2]}")
