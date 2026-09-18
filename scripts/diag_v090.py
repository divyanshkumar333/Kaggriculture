from kaggle_environments import make

env = make('kaggriculture', configuration={'episodeSteps': 96}, debug=False)
env.run(['agents/v090_meta_adaptive.py', 'agents/v057_generalized_spoiler.py'])

for step_idx, step in enumerate(env.steps):
    obs = step[0].observation
    day = obs['day']
    hour = obs['hour']
    m0 = obs['farms'][0]['money']
    m1 = obs['farms'][1]['money']
    if hour == 0 or step_idx <= 5:
        tiles = obs['farms'][0]['tiles']
        animals = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get('animal'))
        weeds = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get('kind') == 'WEED')
        action = step[0].action or {}
        print(f"Day {day} Hr {hour} | P0=${m0:.0f} P1=${m1:.0f} | animals={animals} weeds={weeds}")
        print(f"  market: {action.get('market', [])}")
