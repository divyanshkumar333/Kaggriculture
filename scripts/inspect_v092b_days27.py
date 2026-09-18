"""Trace Days 2-7 market ops of v092b to see fertilizer selling and seed buying."""
import json, base64, zlib

with open('agents/v092b_replay_seed.py', 'r') as f:
    code = f.read()

start = code.find("b85decode(\n    '") + len("b85decode(\n    '")
end = code.find("'", start)
b85_str = code[start:end]
actions = json.loads(zlib.decompress(base64.b85decode(b85_str)))

print("=== Days 2-7 market ops ===")
for i, a in enumerate(actions[48:200]):
    step = i + 48
    day = step // 24
    hour = step % 24
    market = a.get('market', [])
    if market:
        print(f"  D{day}H{hour}: market={market}")

print("\n=== Days 2-7 farmer actions (non-PASS) ===")
for i, a in enumerate(actions[48:200]):
    step = i + 48
    day = step // 24
    hour = step % 24
    farmer = a.get('farmer', ['PASS'])
    hands = [h for h in a.get('hands', []) if h and h != ['PASS']]
    if farmer != ['PASS'] or hands:
        if hour == 0:
            print(f"  -- Day {day} --")
        print(f"  D{day}H{hour}: farmer={farmer} hands={hands[:4]}")
