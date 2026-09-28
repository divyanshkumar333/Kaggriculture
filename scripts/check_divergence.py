import sys, json, zlib, base64
with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
end = content.index("'", start)
raw = zlib.decompress(base64.b85decode(content[start:end]))
data = json.loads(raw)

routes = data['routes']
r105 = routes['105']
r123 = routes['123']

divergence_step = -1
for step in range(len(r105)):
    if r105[step] != r123[step]:
        divergence_step = step
        break

print(f"Route 105 and Route 123 diverge at step {divergence_step} (Day {divergence_step//24})")
