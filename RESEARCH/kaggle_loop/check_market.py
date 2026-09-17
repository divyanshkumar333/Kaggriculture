import json
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=False)
    env.run(['agents/v060_melon_frontrunner.py', 'agents/v060_melon_frontrunner.py'])
    
    buys = set()
    sells = set()
    for step in env.steps:
        obs = step[0].observation
        if obs:
            for action in step[0].action.get('market', []):
                if action[0] == 'BUY_PRODUCT':
                    buys.add(action[1])
                elif action[0] == 'SELL':
                    sells.add(action[1])
                    
    print("Market actions:", buys, sells)
    
if __name__ == "__main__":
    main()
