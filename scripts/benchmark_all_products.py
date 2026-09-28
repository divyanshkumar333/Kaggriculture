"""
Benchmark all products sold by all 41 routes to understand where low-output routes make money.
"""
import sys, json, zlib, base64
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

route_shops = {}
for shop_entry in shops:
    rid = str(shop_entry['route'])
    if rid not in route_shops:
        route_shops[rid] = []
    route_shops[rid].append(tuple(shop_entry['shops']))

print("=== ALL PRODUCE SALES (Days 10-20) ===")
print(f"{'Route':5} {'MILK':>5} {'WOOL':>5} {'STRAW':>5} {'MELON':>5} {'WHEAT':>5} {'CARROT':>6} {'TOMATO':>6} {'EGG':>5} {'Trigger'}")

for route_id in sorted(routes.keys(), key=lambda x: int(x)):
    route = routes[route_id]
    
    counts = {'MILK':0, 'WOOL':0, 'STRAWBERRY':0, 'MELON':0, 'WHEAT':0, 'CARROT':0, 'TOMATO':0, 'EGG':0}
    for step in range(240, min(480, len(route))):
        action_idx = route[step]
        if action_idx >= len(actions):
            continue
        mkt = actions[action_idx].get('market', [])
        for o in mkt:
            if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                if o[1] in counts:
                    counts[o[1]] += int(o[2])
    
    triggers = route_shops.get(route_id, [])
    trigger_str = str(triggers[0]) if triggers else 'DEFAULT'
    
    print(f"{route_id:5} {counts['MILK']:5d} {counts['WOOL']:5d} {counts['STRAWBERRY']:5d} {counts['MELON']:5d} {counts['WHEAT']:5d} {counts['CARROT']:6d} {counts['TOMATO']:6d} {counts['EGG']:5d} {trigger_str}")
