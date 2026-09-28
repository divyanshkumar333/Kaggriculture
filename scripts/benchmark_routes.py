"""
Benchmark all 41 routes: run each route against 'pass' opponent for 5 seeds each.
Identify the highest-scoring routes to understand which shop configs are best.
"""
import sys, json, zlib, base64, re
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')

from kaggle_environments import make
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

# For each route, figure out what shops trigger it
route_shops = {}  # route_id -> list of shop tuples
for shop_entry in shops:
    rid = str(shop_entry['route'])
    if rid not in route_shops:
        route_shops[rid] = []
    route_shops[rid].append(tuple(shop_entry['shops']))

# What routes exist and what their total sell volumes look like
# (from the compressed action tape)
print("=== ROUTE ANALYSIS: Key differences in mid-game sells ===")
print(f"{'Route':8} {'Days10-20 MILK':>14} {'Days10-20 WOOL':>14} {'Days10-20 STRAW':>15} {'Shop trigger':>30}")
print("-" * 90)

for route_id in sorted(routes.keys(), key=lambda x: int(x)):
    route = routes[route_id]
    
    # Sum sells of MILK, WOOL, STRAWBERRY in days 10-20 (steps 240-480)
    milk = wool = straw = 0
    for step in range(240, min(480, len(route))):
        action_idx = route[step]
        if action_idx >= len(actions):
            continue
        mkt = actions[action_idx].get('market', [])
        for o in mkt:
            if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                if o[1] == 'MILK':
                    milk += int(o[2])
                elif o[1] == 'WOOL':
                    wool += int(o[2])
                elif o[1] == 'STRAWBERRY':
                    straw += int(o[2])
    
    # Shop triggers
    triggers = route_shops.get(route_id, [])
    trigger_str = str(triggers[0]) if triggers else 'DEFAULT'
    
    print(f"Route {route_id:4}: MILK={milk:6d}  WOOL={wool:6d}  STRAW={straw:6d}  {trigger_str}")

# Save for later
result = {}
for route_id in sorted(routes.keys(), key=lambda x: int(x)):
    route = routes[route_id]
    sells = {}
    for step in range(0, min(720, len(route))):
        action_idx = route[step]
        if action_idx >= len(actions):
            continue
        mkt = actions[action_idx].get('market', [])
        for o in mkt:
            if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                item = o[1]
                qty = int(o[2])
                sells[item] = sells.get(item, 0) + qty
    result[route_id] = {
        'sells': sells,
        'shop_triggers': [list(t) for t in route_shops.get(route_id, [])],
    }

Path(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\route_sells.json').write_text(
    json.dumps(result, indent=2), encoding='utf-8'
)
print("\nSaved to route_sells.json")
