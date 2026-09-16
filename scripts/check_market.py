import json
import base64
import zlib
with open('agents/public_v16_rc5.py') as f:
    text = f.read()
b85_data = text.split("base64.b85decode('")[1].split("')")[0]
actions = json.loads(zlib.decompress(base64.b85decode(b85_data)).decode('utf-8'))
for i in range(480, 720):
    for order in actions[i].get('market', []):
        if order[0] == 'SELL' and order[1] == 'STRAWBERRY':
            print(f'Day {i // 24} Hour {i % 24}:', order)
