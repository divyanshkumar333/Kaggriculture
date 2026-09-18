import json

with open('episode-110135509-replay.json', 'r') as f:
    data = json.load(f)
steps = data['steps']

winner = 0  # P0 won with 156567
for step_idx in [0, 1, 2, 3, 4, 5, 12, 24, 25, 48]:
    if step_idx >= len(steps): break
    obs = steps[step_idx][winner]['observation']
    tiles = obs['farms'][winner]['tiles']
    farm = obs['farms'][winner]
    farmer = farm['farmer']
    hands = farm['hands']
    pastures = [(c, r) for r, row in enumerate(tiles) for c, t in enumerate(row) 
                if isinstance(t, dict) and t.get('kind') == 'PASTURE']
    animals_on = [(c, r, t.get('animal')) for r, row in enumerate(tiles) for c, t in enumerate(row) 
                  if isinstance(t, dict) and t.get('animal')]
    priv = obs['private']
    shed = priv['shed']
    seeds = priv['seeds']
    d = obs['day']
    h = obs['hour']
    print(f"Step {step_idx} D{d}H{h} | farmer={farmer} hands={len(hands)} | pastures={pastures}")
    print(f"  animals_placed={animals_on}")
    print(f"  shed: COW={shed.get('COW',0)} SHEEP={shed.get('SHEEP',0)}")
    action = steps[step_idx][winner].get('action', {})
    fa = action.get('farmer', [])
    ha = action.get('hands', [])
    print(f"  farmer_action={fa}  hand_actions={ha}")
    print()
