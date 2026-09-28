import sys, json, zlib, base64
with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

print('Shop mapping:')
for r in data['shops']:
    print(f'{r["shops"]} -> Route {r["route"]}')
