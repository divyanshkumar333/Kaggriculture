import sys, json, zlib, base64

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

actions = data['actions']
r105 = data['routes']['105']
r123 = data['routes']['123']

with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\episode-113341974-replay.json', 'r') as f:
    replay = json.load(f)

p1_action_167 = replay['steps'][167][1].get('action', {})

print(f"P1 Action at Step 167: {p1_action_167}")

# Compare to Route 105 and 123
a105 = actions[r105[167]]
a123 = actions[r123[167]]

print(f"Route 105 expected at 167: {a105}")
print(f"Route 123 expected at 167: {a123}")
