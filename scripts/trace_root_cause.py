"""
Check if ANY actions differ between V104 and V105 BEFORE step 145.
If not, find what state difference at step 144 makes step 145 diverge.
"""
import sys
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')

from kaggle_environments import make
import importlib.util, json

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

# Find very first divergence
print("Finding FIRST divergence in full game:")
for step_num in range(min(len(env104.steps), len(env105.steps))):
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    m104 = (act104 or {}).get('market', [])
    m105 = (act105 or {}).get('market', [])
    f104 = (act104 or {}).get('farmer', [])
    f105 = (act105 or {}).get('farmer', [])
    h104 = (act104 or {}).get('hands', [])
    h105 = (act105 or {}).get('hands', [])
    
    if m104 != m105 or f104 != f105 or h104 != h105:
        obs104 = env104.steps[step_num][0].get('observation', {})
        obs105 = env105.steps[step_num][0].get('observation', {})
        cash104 = obs104.get('farms', [{}])[0].get('money', 0)
        cash105 = obs105.get('farms', [{}])[0].get('money', 0)
        shed104 = obs104.get('private', {}).get('shed', {})
        shed105 = obs105.get('private', {}).get('shed', {})
        print(f"FIRST DIVERGENCE at Step {step_num} (Day {step_num//24}h{step_num%24})")
        print(f"  Cash104={cash104:.0f}  Cash105={cash105:.0f}")
        print(f"  Shed104={shed104}  Shed105={shed105}")
        print(f"  V104 action: farmer={f104} market={m104}")
        print(f"  V105 action: farmer={f105} market={m105}")
        break

# Now check the state AT step 144 vs 145
print("\n=== STATE AT STEP 144 (just before divergence) ===")
for step_num in [144, 145]:
    obs104 = env104.steps[step_num][0].get('observation', {})
    obs105 = env105.steps[step_num][0].get('observation', {})
    
    cash104 = obs104.get('farms', [{}])[0].get('money', 0)
    cash105 = obs105.get('farms', [{}])[0].get('money', 0)
    shed104 = obs104.get('private', {}).get('shed', {})
    shed105 = obs105.get('private', {}).get('shed', {})
    seeds104 = obs104.get('private', {}).get('seeds', {})
    seeds105 = obs105.get('private', {}).get('seeds', {})
    
    print(f"\nStep {step_num}:")
    print(f"  V104: cash={cash104:.0f} shed={shed104} seeds={seeds104}")
    print(f"  V105: cash={cash105:.0f} shed={shed105} seeds={seeds105}")
    
    # What action did V104 take at step 144?
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    if step_num == 144:
        print(f"  V104 action: {act104}")
        print(f"  V105 action: {act105}")

# Look for any divergence 100 steps earlier
print("\n=== CHECKING FOR DIVERGENCE IN STEPS 0-143 ===")
diffs_before = []
for step_num in range(144):
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    if act104 != act105:
        diffs_before.append(step_num)

if not diffs_before:
    print("NO DIVERGENCE in steps 0-143! Actions are IDENTICAL.")
    print("This means the route selection at step 145 is PURELY observation-driven.")
    print("Both V104 and V105 see DIFFERENT observations at step 145, despite identical prior actions.")
    print("This is impossible unless... there is non-determinism or the random opponent matters.")
else:
    print(f"Divergences found at: {diffs_before[:20]}")
