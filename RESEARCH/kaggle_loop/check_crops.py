import json
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=False)
    env.run(['agents/v060_melon_frontrunner.py', 'agents/v060_melon_frontrunner.py'])
    
    plants = set()
    for step in env.steps:
        obs = step[0].observation
        if obs:
            for row in obs['farms'][0]['tiles']:
                for t in row:
                    if type(t) == dict and t.get('kind') == 'PLANT':
                        plants.add(t.get('crop'))
                        
    print("All Plants in Match for P0:", plants)
    
if __name__ == "__main__":
    main()
