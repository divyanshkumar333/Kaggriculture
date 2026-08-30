import json
import os
import glob

def analyze_replay(path):
    with open(path, 'r') as f:
        data = json.load(f)
    print('================================================================================')
    print('ANALYZING REPLAY:', os.path.basename(path))
    steps = data['steps']
    
    for day in range(30):
        # hour 1 of each day to see post-morning actions/hires
        step_idx = day * 24 + 2
        if step_idx >= len(steps):
            step_idx = len(steps) - 1
        obs0 = steps[step_idx][0]['observation']
        farms = obs0['farms']
        market = obs0.get('market', {})
        prices = market.get('prices', {})
        inventory = market.get('inventory', {})
        
        def count_tiles(farm):
            plants = {}
            animals = {}
            structures = {}
            unlocked = len(farm.get('unlocked_quadrants', []))
            for row in farm['tiles']:
                for t in row:
                    if isinstance(t, dict):
                        kind = t.get('kind')
                        if kind == 'PLANT':
                            crop = t.get('crop')
                            plants[crop] = plants.get(crop, 0) + 1
                        elif kind in ('COOP', 'PASTURE'):
                            structures[kind] = structures.get(kind, 0) + 1
                            if t.get('animal'):
                                a = t.get('animal')
                                animals[a] = animals.get(a, 0) + 1
            return {
                'unlocked_quads': unlocked, 
                'money': farm['money'], 
                'plants': plants, 
                'animals': animals, 
                'structures': structures, 
                'hands': len(farm['hands'])
            }
        
        c0 = count_tiles(farms[0])
        c1 = count_tiles(farms[1])
        if day in (0, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29):
            print(f'Day {day:2d} (step {step_idx}):')
            print(f'  P0: money={c0["money"]:7.0f} | hands={c0["hands"]} | quads={c0["unlocked_quads"]} | plants={c0["plants"]} | animals={c0["animals"]}')
            print(f'  P1: money={c1["money"]:7.0f} | hands={c1["hands"]} | quads={c1["unlocked_quads"]} | plants={c1["plants"]} | animals={c1["animals"]}')
            print(f'  Market Prices: W={prices.get("WHEAT")} C={prices.get("CARROT")} T={prices.get("TOMATO")} S={prices.get("STRAWBERRY")} M={prices.get("MELON")} Egg={prices.get("EGG")} Milk={prices.get("MILK")} Wool={prices.get("WOOL")}')

    final_0 = steps[-1][0]['reward']
    final_1 = steps[-1][1]['reward']
    print('--------------------------------------------------------------------------------')
    print(f'FINAL REWARD: P0 = {final_0} | P1 = {final_1} (Winner: {"P0" if final_0 > final_1 else "P1" if final_1 > final_0 else "Tie"})')
    print('================================================================================\n')

if __name__ == '__main__':
    for path in sorted(glob.glob('kaggle_episodes/*-replay.json')):
        analyze_replay(path)
