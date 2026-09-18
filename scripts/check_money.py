from kaggle_environments import make

env = make('kaggriculture', configuration={'episodeSteps': 6}, debug=False)
env.run(['agents/v090_meta_adaptive.py', 'random'])

for step_idx, step in enumerate(env.steps):
    obs0 = step[0]['observation']
    money = obs0['farms'][0]['money']
    seeds = obs0['private']['seeds']
    shed = obs0['private']['shed']
    action = step[0].get('action') or {}
    print(f"Step {step_idx}: money=${money} seeds={dict(seeds)} shed_animals=COW={shed.get('COW',0)} SHEEP={shed.get('SHEEP',0)}")
    print(f"  action_market: {action.get('market', [])}")
