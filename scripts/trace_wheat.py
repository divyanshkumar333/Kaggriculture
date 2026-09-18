from kaggle_environments import make

env = make('kaggriculture', configuration={'episodeSteps': 48}, debug=False)
env.run(['agents/v090_meta_adaptive.py', 'random'])

for s, step in enumerate(env.steps[:10]):
    obs = step[0]['observation']
    m = obs['farms'][0]['money']
    wp = obs['market']['prices'].get('WHEAT', 25)
    wi = obs['market']['inventory'].get('WHEAT', 10000)
    shed = obs['private']['shed']
    invs = obs['private']['inventories']
    w_shed = shed.get('WHEAT', 0)
    w_inv = sum(iv.get('WHEAT', 0) for iv in invs if isinstance(iv, dict))
    action = step[0].get('action') or {}
    print(f"Step {s}: money=${m:.0f} wheat_price=${wp} wheat_inv={wi} wheat_we_have={w_shed+w_inv}(shed={w_shed},inv={w_inv})")
    if action.get('market'):
        print(f"  market: {action['market']}")
