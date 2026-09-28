"""
Find which route V105 took in the losing episode vs which the opponent took.
The key fingerprint: V105 does SELL WHEAT 5 -> BUY WHEAT 5 oscillation Day 0 Steps 2-21.
"""
import json, zlib, base64
from pathlib import Path

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

actions = data['actions']
routes = data['routes']
shops = data['shops']

# Find the "wheat oscillation" route - does SELL WHEAT then BUY WHEAT alternating
print("=== ROUTES WITH WHEAT OSCILLATION (sell then buy alternating in Day 0) ===")
oscillation_routes = []
for route_id, route in routes.items():
    # Check steps 2-20 for alternating sell/buy wheat
    oscillations = 0
    for i in range(2, min(22, len(route))):
        action_idx = route[i]
        if action_idx >= len(actions):
            continue
        mkt = actions[action_idx].get('market', [])
        for order in mkt:
            if isinstance(order, list) and len(order) > 1:
                if order[0] == 'SELL' and order[1] == 'WHEAT':
                    oscillations += 1
    if oscillations >= 5:
        # This route has wheat oscillation
        # Get full Day 0 opening
        day0 = []
        for action_idx in route[:24]:
            if action_idx < len(actions):
                mkt = actions[action_idx].get('market', [])
                if mkt:
                    day0.append(mkt)
        oscillation_routes.append(route_id)
        print(f"Route {route_id}: {oscillations} sell-wheat turns in steps 2-21")
        print(f"  Day 0 market sequence (first 5 turns):")
        for i, m in enumerate(day0[:6]):
            print(f"    Step {i+1}: {m}")

if not oscillation_routes:
    print("No oscillation routes found - checking what route triggers step 1 opening")

# Check the actual step 1 action for V105's route
# V105 Day 0 Step 1: [HIRE x4, BUY PRODUCT WHEAT 5, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 4, BUY_SEED MELON 5, BUY_SEED WHEAT 5]
print("\n=== FINDING ROUTE MATCHING V105's ACTUAL OPENING ===")
v105_opening_step1 = ['HIRE', 'HIRE', 'HIRE', 'HIRE', 'BUY_PRODUCT WHEAT 5', 'BUY_ANIMAL COW 1', 'BUY_ANIMAL SHEEP 4', 'BUY_SEED MELON 5', 'BUY_SEED WHEAT 5']

for route_id, route in routes.items():
    if len(route) < 2:
        continue
    action_idx = route[1]
    if action_idx >= len(actions):
        continue
    mkt = actions[action_idx].get('market', [])
    
    # Check for COW=1, SHEEP=4, MELON=5 
    animals = {}
    seeds = {}
    hires = 0
    for order in mkt:
        if isinstance(order, list) and order:
            if order[0] == 'HIRE':
                hires += 1
            elif order[0] == 'BUY_ANIMAL' and len(order) > 1:
                animals[order[1]] = animals.get(order[1], 0) + (order[2] if len(order) > 2 else 1)
            elif order[0] == 'BUY_SEED' and len(order) > 1:
                seeds[order[1]] = seeds.get(order[1], 0) + (order[2] if len(order) > 2 else 1)
    
    if animals.get('COW', 0) == 1 and animals.get('SHEEP', 0) == 4:
        print(f"Route {route_id}: Step 1 -> hires={hires} animals={animals} seeds={seeds}")
        # Show more of this route
        print(f"  Steps 2-5:")
        for i in range(2, 6):
            if i < len(route):
                idx = route[i]
                if idx < len(actions):
                    print(f"    Step {i}: {actions[idx].get('market', [])}")

print("\n=== ROUTES BY ANIMAL OPENING ===")
animal_patterns = {}
for route_id, route in routes.items():
    animals = {}
    for action_idx in route[:10]:  # First 10 steps
        if action_idx < len(actions):
            mkt = actions[action_idx].get('market', [])
            for o in mkt:
                if isinstance(o, list) and o and o[0] == 'BUY_ANIMAL' and len(o) > 1:
                    animals[o[1]] = animals.get(o[1], 0) + (o[2] if len(o) > 2 else 1)
    key = f"COW:{animals.get('COW',0)} SHEEP:{animals.get('SHEEP',0)} GOOSE:{animals.get('GOOSE',0)}"
    if key not in animal_patterns:
        animal_patterns[key] = []
    animal_patterns[key].append(route_id)

for pattern, route_ids in sorted(animal_patterns.items()):
    print(f"  {pattern}: Routes {route_ids}")
