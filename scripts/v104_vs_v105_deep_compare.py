"""
Deep analysis of the V104 vs V105 quote_priority difference.
Runs both agents against the same opponent and traces divergent market orders.
"""
import sys, json
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')

from kaggle_environments import make
import importlib.util
import copy

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

v104 = load_agent(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', 'v104')
v105 = load_agent(r'e:\Setup\kaggle\kaggriculture\agents\v105_revert_quote_priority.py', 'v105')

SEEDS = [42, 101, 2024, 777, 9999, 12345, 31337, 88888, 55555, 11111]
N_GAMES = 10

results = []
v104_cash = []
v105_cash = []
divergence_turns = []

for seed in SEEDS:
    # V104 vs random
    env104 = make('kaggriculture', debug=False, configuration={'randomSeed': seed})
    env104.run([v104.agent, 'random'])
    cash104 = env104.steps[-1][0].get('observation', {}).get('farms', [{}])[0].get('money', 0) or 0
    
    # V105 vs random
    env105 = make('kaggriculture', debug=False, configuration={'randomSeed': seed})
    env105.run([v105.agent, 'random'])
    cash105 = env105.steps[-1][0].get('observation', {}).get('farms', [{}])[0].get('money', 0) or 0
    
    v104_cash.append(cash104)
    v105_cash.append(cash105)
    
    # Find first divergent turn
    diverged = False
    first_div = None
    for step_num, (step104, step105) in enumerate(zip(env104.steps, env105.steps)):
        action104 = step104[0].get('action', {})
        action105 = step105[0].get('action', {})
        if action104 and action105 and action104.get('market') != action105.get('market'):
            if not diverged:
                diverged = True
                first_div = {
                    'step': step_num,
                    'v104_market': action104.get('market', []),
                    'v105_market': action105.get('market', []),
                }
    
    divergence_turns.append(first_div)
    print(f'Seed {seed:6d}: V104={cash104:8.0f}  V105={cash105:8.0f}  Diff={cash104-cash105:+8.0f}  FirstDiv=step {first_div["step"] if first_div else "NONE"}')

avg104 = sum(v104_cash)/len(v104_cash)
avg105 = sum(v105_cash)/len(v105_cash)
print(f'\nAverage V104: {avg104:.0f}')
print(f'Average V105: {avg105:.0f}')
print(f'V104 advantage: {avg104-avg105:+.0f}')
print(f'V104 wins: {sum(1 for a,b in zip(v104_cash,v105_cash) if a>b)}/{N_GAMES}')

print('\n=== FIRST DIVERGENCE ANALYSIS ===')
for i, (seed, div) in enumerate(zip(SEEDS, divergence_turns)):
    if div:
        print(f'Seed {seed}: Step {div["step"]}')
        print(f'  V104 market: {div["v104_market"]}')
        print(f'  V105 market: {div["v105_market"]}')
