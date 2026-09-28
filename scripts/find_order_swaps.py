"""
Precise trace: what generates the Step 145 divergence?
The code diff is only the quote_priority sort guard.
But Step 145 shows completely different SELL items (FERTILIZER-only vs WHEAT+FERTILIZER).
This means the sort in EARLIER steps must be changing cash or shed state in a way
that cascades to completely different route/plan decisions by Day 6.

Strategy: run step-by-step and compare sell orders from Step 0 to 145.
"""
import sys
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')

from kaggle_environments import make
import importlib.util

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

v104 = load_agent(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', 'v104')
v105 = load_agent(r'e:\Setup\kaggle\kaggriculture\agents\v105_revert_quote_priority.py', 'v105')

SEED = 101
env104 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})
env105 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})

env104.run([v104.agent, 'random'])
env105.run([v105.agent, 'random'])

# Find ONLY sell-ordering differences (where same sells exist but in different order)
print("=== SELL ORDER DIFFERENCES (Steps 0-145) ===")
print("(Only showing turns where the SAME sells exist but in different order)")
order_diffs = 0
for step_num in range(0, 146):
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    m104 = (act104 or {}).get('market', [])
    m105 = (act105 or {}).get('market', [])
    
    if m104 == m105:
        continue
    
    # Check if this is purely a sell ordering difference
    # (same sells in different order, same non-sells)
    sells104 = [o for o in m104 if isinstance(o, list) and o and o[0] == 'SELL']
    sells105 = [o for o in m105 if isinstance(o, list) and o and o[0] == 'SELL']
    nonsell104 = [o for o in m104 if not (isinstance(o, list) and o and o[0] == 'SELL')]
    nonsell105 = [o for o in m105 if not (isinstance(o, list) and o and o[0] == 'SELL')]
    
    obs104 = env104.steps[step_num][0].get('observation', {})
    cash104 = obs104.get('farms', [{}])[0].get('money', 0)
    obs105 = env105.steps[step_num][0].get('observation', {})
    cash105 = obs105.get('farms', [{}])[0].get('money', 0)
    
    # Sort sells to check if they're the same set
    sells104_sorted = sorted([tuple(o) for o in sells104])
    sells105_sorted = sorted([tuple(o) for o in sells105])
    
    if sells104_sorted == sells105_sorted and nonsell104 == nonsell105:
        order_diffs += 1
        print(f"\nStep {step_num} (Day {step_num//24}h{step_num%24}): PURE SELL ORDER SWAP")
        print(f"  V104 sells: {sells104}")
        print(f"  V105 sells: {sells105}")
        print(f"  Cash104={cash104:.0f}  Cash105={cash105:.0f}")
        
        # This is the KEY: does V104's different ordering extract more/less cash?
        # Calculate the actual revenue from each ordering
        prices = obs104.get('market', {}).get('prices', {})
        print(f"  Market prices: {prices}")
    elif sells104 != sells105:
        # Completely different sell structures
        print(f"\nStep {step_num} (Day {step_num//24}h{step_num%24}): STRUCTURAL SELL DIFFERENCE")
        print(f"  V104 market: {m104[:5]}")
        print(f"  V105 market: {m105[:5]}")
        print(f"  Cash104={cash104:.0f}  Cash105={cash105:.0f}")

print(f"\nTotal pure-order-swap turns found: {order_diffs}")
