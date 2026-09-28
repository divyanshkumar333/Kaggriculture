"""
Trace exactly HOW the quote_priority 1-line change causes route divergence at Step 145.
The hypothesis: earlier sell ordering affects cash at critical buy decisions,
which tips the route-selection logic (router) to pick different animals.
"""
import sys, json
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

# Use seed 101 where they diverge earliest and V104 wins big
SEED = 101

env104 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})
env105 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})

env104.run([v104.agent, 'random'])
env105.run([v105.agent, 'random'])

print(f"Seed {SEED}:")
print(f"V104 final cash: {env104.steps[-1][0].get('observation', {}).get('farms', [{}])[0].get('money', 0):.0f}")
print(f"V105 final cash: {env105.steps[-1][0].get('observation', {}).get('farms', [{}])[0].get('money', 0):.0f}")

print("\n=== STEP-BY-STEP DIVERGENCE TRACE (Steps 130-160) ===")
for step_num in range(130, 165):
    obs104 = env104.steps[step_num][0].get('observation', {})
    obs105 = env105.steps[step_num][0].get('observation', {})
    
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    
    cash104 = obs104.get('farms', [{}])[0].get('money', 0)
    cash105 = obs105.get('farms', [{}])[0].get('money', 0)
    
    m104 = (act104 or {}).get('market', [])
    m105 = (act105 or {}).get('market', [])
    
    diff_marker = " <-- DIVERGE" if m104 != m105 else ""
    cash_marker = f" [cash diff: {cash104-cash105:+.0f}]"
    
    if m104 != m105 or step_num >= 143:
        print(f"\nStep {step_num} (Day {step_num//24}, Hour {step_num%24}):{cash_marker}{diff_marker}")
        print(f"  Cash104={cash104:.0f}  Cash105={cash105:.0f}")
        if m104 != m105:
            print(f"  V104 market: {m104}")
            print(f"  V105 market: {m105}")
        else:
            # Show sells only if they exist
            sells = [o for o in m104 if isinstance(o, list) and o and o[0] == 'SELL']
            if sells:
                print(f"  Common market: {m104}")

print("\n=== SELL ORDER ANALYSIS (Steps 0-145) ===")
print("Looking for turns where V104 and V105 generate different SELL orderings...")
for step_num in range(0, 146):
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    m104 = (act104 or {}).get('market', [])
    m105 = (act105 or {}).get('market', [])
    
    if m104 != m105:
        # Check if this is ONLY a sell ordering difference vs different orders entirely  
        sells104 = sorted(str(o) for o in m104 if isinstance(o, list) and o and o[0] == 'SELL')
        sells105 = sorted(str(o) for o in m105 if isinstance(o, list) and o and o[0] == 'SELL')
        nonsell104 = [o for o in m104 if not (isinstance(o, list) and o and o[0] == 'SELL')]
        nonsell105 = [o for o in m105 if not (isinstance(o, list) and o and o[0] == 'SELL')]
        
        obs104 = env104.steps[step_num][0].get('observation', {})
        cash104 = obs104.get('farms', [{}])[0].get('money', 0)
        obs105 = env105.steps[step_num][0].get('observation', {})
        cash105 = obs105.get('farms', [{}])[0].get('money', 0)
        
        print(f"\nStep {step_num} (Day {step_num//24}h{step_num%24}): cash104={cash104:.0f} cash105={cash105:.0f}")
        if sells104 == sells105 and nonsell104 == nonsell105:
            print(f"  PURE ORDER SWAP: {m104} -> {m105}")
        elif sells104 == sells105:
            print(f"  Non-sell order difference:")
            print(f"    V104: {m104}")
            print(f"    V105: {m105}")
        else:
            print(f"  STRUCTURAL DIFFERENCE:")
            print(f"    V104: {m104}")
            print(f"    V105: {m105}")
