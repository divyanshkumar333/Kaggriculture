"""
Count BUY_SEED, BUY_ANIMAL, and BUILD operations in the routes to see what the routes ACTUALLY build/plant.
"""
import sys, json, zlib, base64

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

actions = data['actions']
routes = data['routes']

print("=== WHAT DO THE ROUTES ACTUALLY BUILD/PLANT? ===")
print(f"{'Route':5} {'MELON':>6} {'STRAW':>6} {'TOMATO':>6} {'CARROT':>6} {'WHEAT':>6} | {'COW':>4} {'SHEEP':>5} {'GOOSE':>5}")

for route_id in sorted(routes.keys(), key=lambda x: int(x)):
    route = routes[route_id]
    
    seeds = {'MELON':0, 'STRAWBERRY':0, 'TOMATO':0, 'CARROT':0, 'WHEAT':0}
    animals = {'COW':0, 'SHEEP':0, 'GOOSE':0}
    
    for step in range(len(route)):
        action_idx = route[step]
        if action_idx >= len(actions):
            continue
        
        act = actions[action_idx]
        
        # Check market for BUY_SEED and BUY_ANIMAL
        for o in act.get('market', []):
            if isinstance(o, list) and len(o) >= 3:
                if o[0] == 'BUY_SEED':
                    crop = o[1]
                    qty = int(o[2])
                    if crop in seeds: seeds[crop] += qty
                elif o[0] == 'BUY_ANIMAL':
                    animal = o[1]
                    qty = int(o[2])
                    if animal in animals: animals[animal] += qty

    print(f"{route_id:5} {seeds['MELON']:6d} {seeds['STRAWBERRY']:6d} {seeds['TOMATO']:6d} {seeds['CARROT']:6d} {seeds['WHEAT']:6d} | {animals['COW']:4d} {animals['SHEEP']:5d} {animals['GOOSE']:5d}")
