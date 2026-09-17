import json
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=False)
    env.run(['agents/v060_melon_frontrunner.py', 'agents/v060_melon_frontrunner.py'])
    
    for step in env.steps:
        obs = step[0].observation
        if obs:
            for action in step[0].action.get('market', []):
                if action[0] == 'SELL' and action[1] == 'MELON':
                    print(f"Step {obs['step']} P0 sold {action[2]} MELON. Shed: {obs['private']['shed']}")
                    
if __name__ == "__main__":
    main()
