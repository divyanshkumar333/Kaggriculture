"""Compare v092b seed vs v093_evolved_best action-by-action to see what changed."""
import json, base64, zlib

def load_trace(path):
    with open(path, 'r') as f:
        code = f.read()
    start = code.find("b85decode(\n    '") + len("b85decode(\n    '")
    end = code.find("'", start)
    return json.loads(zlib.decompress(base64.b85decode(code[start:end])))

seed = load_trace('agents/v092b_replay_seed.py')
best = load_trace('agents/v093_evolved_best.py')

print("=== Differences (v092b seed vs v093_evolved_best) ===")
diffs = 0
for i, (s, b) in enumerate(zip(seed, best)):
    if s != b:
        day = i // 24
        hour = i % 24
        diffs += 1
        if diffs <= 30:  # show first 30 differences
            print(f"  D{day}H{hour}:")
            if s.get('farmer') != b.get('farmer'):
                print(f"    farmer: {s.get('farmer')} -> {b.get('farmer')}")
            if s.get('market') != b.get('market'):
                print(f"    market: {s.get('market')} -> {b.get('market')}")
            for hi, (sh, bh) in enumerate(zip(s.get('hands', []), b.get('hands', []))):
                if sh != bh:
                    print(f"    hand[{hi}]: {sh} -> {bh}")

print(f"\nTotal differences: {diffs}")
