from kaggle_environments import make

env = make('kaggriculture', configuration={'episodeSteps': 240}, debug=False)
env.run(['agents/v090_meta_adaptive.py', 'random'])

for step_idx, step in enumerate(env.steps):
    obs0 = step[0]['observation']
    day = obs0['day']
    hour = obs0['hour']
    if hour != 0 and step_idx > 0: continue
    money = obs0['farms'][0]['money']
    tiles = obs0['farms'][0]['tiles']
    pastures = [(c, r) for r, row in enumerate(tiles) for c, t in enumerate(row)
                if isinstance(t, dict) and t.get('kind') == 'PASTURE']
    animals = [(c, r, t.get('animal')) for r, row in enumerate(tiles) for c, t in enumerate(row)
               if isinstance(t, dict) and t.get('animal')]
    plants = [(c, r, t.get('crop')) for r, row in enumerate(tiles) for c, t in enumerate(row)
              if isinstance(t, dict) and t.get('kind') == 'PLANT']
    weeds = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get('kind') == 'WEED')
    shed = obs0['private']['shed']
    fert = shed.get('FERTILIZER', 0)
    wool = shed.get('WOOL', 0)
    milk = shed.get('MILK', 0)
    print(f"D{day}H{hour} money=${money:.0f} | pastures={len(pastures)} animals={len(animals)} plants={len(plants)} weeds={weeds} | fert={fert} wool={wool} milk={milk}")
    if len(animals) < 3 or money < 100:
        print(f"  animals: {animals}")
        print(f"  pastures: {pastures}")
        print(f"  shed: {dict(shed)}")
