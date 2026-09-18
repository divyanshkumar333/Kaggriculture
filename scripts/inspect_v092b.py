"""Trace the first 48 steps of the v092b replay seed to see exact farm actions."""
import json, base64, zlib

with open('agents/v092b_replay_seed.py', 'r') as f:
    code = f.read()

start = code.find("b85decode(\n    '") + len("b85decode(\n    '")
end = code.find("'", start)
b85_str = code[start:end]
actions = json.loads(zlib.decompress(base64.b85decode(b85_str)))

print(f"Total actions: {len(actions)}")
print("\n=== First 48 steps (Day 0-1) ===")
for i, a in enumerate(actions[:48]):
    farmer = a.get('farmer', ['PASS'])
    hands = a.get('hands', [])
    market = a.get('market', [])
    day = i // 24
    hour = i % 24
    non_pass_farmer = farmer if farmer != ['PASS'] else None
    non_pass_hands = [h for h in hands if h != ['PASS']]
    if market or non_pass_farmer or non_pass_hands:
        print(f"  D{day}H{hour}: farmer={farmer} hands={hands[:3]} market={market}")
