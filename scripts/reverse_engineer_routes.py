"""
Reverse engineer the R108 route table to understand:
1. What routes exist (41 total)
2. What each route's opening sequence looks like
3. Which routes match the dominant 2000+ strategy (COW+SHEEP+MELON Day 0)
4. Which shops trigger which routes
"""
import json, zlib, base64, re
from pathlib import Path

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

# Decompress _R108_DATA
idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

actions = data['actions']   # List of 3982 action dicts
routes = data['routes']     # Dict of route_id -> list of action indices  
shops = data['shops']       # List of {shops: [...], route: N}

print(f"Actions: {len(actions)}")
print(f"Routes: {len(routes)} routes (keys: {sorted(routes.keys())[:10]}...)")
print(f"Shop mappings: {len(shops)}")

# Analyze shop-to-route mapping
print("\n=== SHOP -> ROUTE MAPPING (first 20) ===")
for entry in shops[:20]:
    print(f"  Shops {entry['shops']} → Route {entry['route']}")

# Find the route that matches the 2000+ agent's Day 0 opening
# (BUY_ANIMAL COW 2, BUY_ANIMAL SHEEP 2, BUY_SEED MELON X)
print("\n=== ROUTE OPENINGS (first 10 routes) ===")
for route_id in sorted(routes.keys())[:15]:
    route = routes[route_id]
    # Get Day 0 actions (steps 0-23)
    day0_markets = []
    for action_idx in route[:24]:
        if action_idx < len(actions):
            mkt = actions[action_idx].get('market', [])
            buys = [o for o in mkt if isinstance(o, list) and o and o[0] in ('BUY_SEED', 'BUY_ANIMAL', 'BUY_LAND')]
            day0_markets.extend(buys)
    
    # Summarize animal and seed buys on Day 0
    animals = {}
    seeds = {}
    for buy in day0_markets:
        if buy[0] == 'BUY_ANIMAL':
            animal = buy[1] if len(buy) > 1 else '?'
            qty = buy[2] if len(buy) > 2 else 1
            animals[animal] = animals.get(animal, 0) + qty
        elif buy[0] == 'BUY_SEED':
            seed = buy[1] if len(buy) > 1 else '?'
            qty = buy[2] if len(buy) > 2 else 1
            seeds[seed] = seeds.get(seed, 0) + qty
    
    print(f"\nRoute {route_id}: {len(route)} steps")
    print(f"  Day 0 animals: {dict(animals)}")
    print(f"  Day 0 seeds: {dict(seeds)}")

# Which routes have COW + SHEEP + MELON on Day 0?
print("\n=== ROUTES WITH COW+SHEEP+MELON DAY 0 OPENING ===")
cow_sheep_melon_routes = []
for route_id in routes.keys():
    route = routes[route_id]
    animals = {}
    seeds = {}
    for action_idx in route[:48]:  # First 2 days
        if action_idx < len(actions):
            mkt = actions[action_idx].get('market', [])
            for o in mkt:
                if isinstance(o, list) and o:
                    if o[0] == 'BUY_ANIMAL' and len(o) > 1:
                        animals[o[1]] = animals.get(o[1], 0) + (o[2] if len(o) > 2 else 1)
                    elif o[0] == 'BUY_SEED' and len(o) > 1:
                        seeds[o[1]] = seeds.get(o[1], 0) + (o[2] if len(o) > 2 else 1)
    
    has_cow = animals.get('COW', 0) >= 2
    has_sheep = animals.get('SHEEP', 0) >= 2
    has_melon = seeds.get('MELON', 0) >= 5
    
    if has_cow and has_sheep and has_melon:
        cow_sheep_melon_routes.append({
            'id': route_id,
            'animals': animals,
            'seeds': seeds,
        })
        print(f"Route {route_id}: Animals={dict(animals)} Seeds(melon={seeds.get('MELON',0)}, wheat={seeds.get('WHEAT',0)})")

print(f"\nTotal COW+SHEEP+MELON routes: {len(cow_sheep_melon_routes)}")

# What shops trigger these routes?
print("\n=== SHOP TRIGGERS FOR COW+SHEEP+MELON ROUTES ===")
csm_route_ids = {r['id'] for r in cow_sheep_melon_routes}
for shop_entry in shops:
    if str(shop_entry['route']) in csm_route_ids:
        print(f"  Shops {shop_entry['shops']} → Route {shop_entry['route']}")

# Save summary
out = {
    'n_routes': len(routes),
    'n_shops': len(shops),
    'cow_sheep_melon_routes': cow_sheep_melon_routes,
    'shop_triggers': [s for s in shops if str(s['route']) in csm_route_ids]
}
Path(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\route_analysis.json').write_text(
    json.dumps(out, indent=2), encoding='utf-8'
)
print("\nSaved route analysis to route_analysis.json")
