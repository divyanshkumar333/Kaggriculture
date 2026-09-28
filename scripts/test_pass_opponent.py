"""
The CRITICAL proof: V104 and V105 produce identical actions up to step 144,
but diverge at step 145 on ANIMAL CHOICE. Same observations (cash, shed, seeds).
The divergence must come from the OPPONENT's actions (visible in farms[1]) or
the town shop state (visible in town.unlocked_shops).

This test: run with a PASS opponent to eliminate opponent variation.
If they still diverge -> Python hash-based internal non-determinism.
If they DON'T diverge -> the divergence is from seeing different opponent tiles.
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

# Run against PASS opponent (fully deterministic opponent)
env104 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})
env105 = make('kaggriculture', debug=False, configuration={'randomSeed': SEED})

env104.run([v104.agent, 'pass'])
env105.run([v105.agent, 'pass'])

print("=== WITH PASS OPPONENT ===")
print(f"V104 final cash: {env104.steps[-1][0]['observation']['farms'][0]['money']:.0f}")
print(f"V105 final cash: {env105.steps[-1][0]['observation']['farms'][0]['money']:.0f}")

# Find first divergence
for step_num in range(min(len(env104.steps), len(env105.steps))):
    act104 = env104.steps[step_num][0].get('action', {})
    act105 = env105.steps[step_num][0].get('action', {})
    if act104 != act105:
        obs104 = env104.steps[step_num][0].get('observation', {})
        obs105 = env105.steps[step_num][0].get('observation', {})
        cash104 = obs104.get('farms', [{}])[0].get('money', 0)
        cash105 = obs105.get('farms', [{}])[0].get('money', 0)
        town104 = obs104.get('town', {}).get('unlocked_shops', [])
        town105 = obs105.get('town', {}).get('unlocked_shops', [])
        opp104 = obs104.get('farms', [{}, {}])[1] if len(obs104.get('farms', [])) > 1 else {}
        opp105 = obs105.get('farms', [{}, {}])[1] if len(obs105.get('farms', [])) > 1 else {}
        print(f"\nFIRST DIVERGENCE at Step {step_num} (Day {step_num//24}h{step_num%24})")
        print(f"  Cash104={cash104:.0f}  Cash105={cash105:.0f}")
        print(f"  Town104={town104}  Town105={town105}")
        print(f"  OppCash104={opp104.get('money', 0):.0f}  OppCash105={opp105.get('money', 0):.0f}")
        print(f"  V104 action: {act104}")
        print(f"  V105 action: {act105}")
        
        # Is it the same cash but different town shops?
        if cash104 == cash105 and town104 != town105:
            print("  --> TOWN SHOP DIFFERENCE causes divergence!")
        elif cash104 == cash105 and town104 == town105:
            print("  --> IDENTICAL STATE but different choices -> Python hash non-determinism!")
        break
else:
    print("No divergence found - V104 and V105 produce identical actions against PASS!")

# Now check the critical step 145 specifically
print("\n=== CHECKING STEP 145 WITH PASS OPPONENT ===")
step145_104 = env104.steps[145]
step145_105 = env105.steps[145]
obs104 = step145_104[0]['observation']
obs105 = step145_105[0]['observation']
print(f"Step 145 V104 observation hash (town, farms):")
print(f"  Town: {obs104.get('town', {})}")
print(f"  OppFarm money: {obs104.get('farms', [{},{}])[1].get('money', 0)}")
print(f"Step 145 V105 observation hash (town, farms):")
print(f"  Town: {obs105.get('town', {})}")
print(f"  OppFarm money: {obs105.get('farms', [{},{}])[1].get('money', 0)}")
