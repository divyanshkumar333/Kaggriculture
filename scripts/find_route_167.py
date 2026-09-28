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

with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\episode-113341974-replay.json', 'r') as f:
    replay = json.load(f)

p1_action_167 = replay['steps'][167][1].get('action', {})

# Find any route that matches this action at step 167
matches = []
for rid, route in routes.items():
    if actions[route[167]] == p1_action_167:
        matches.append(rid)
        
print(f"Routes matching P1 at step 167: {matches}")
