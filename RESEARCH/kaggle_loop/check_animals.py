import json
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=False)
    env.run(['agents/v060_melon_frontrunner.py', 'agents/v060_melon_frontrunner.py'])
    
    animals = set()
    for step in env.steps:
        obs = step[0].observation
        if obs:
            for row in obs['farms'][0]['tiles']:
                for t in row:
                    if type(t) == dict and 'animal' in t:
                        animals.add(t.get('animal'))
                        
    print("All Animals in Match for P0:", animals)
    
if __name__ == "__main__":
    main()
