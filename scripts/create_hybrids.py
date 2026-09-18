"""
Create hybrid agent: 013's opening (Days 0-5) + v092b's mid-game scaling (Days 6-15) + 013's endgame.

The idea: v092b has a superior Days 6-12 sequence (sells wool batch on Day 6,
buys land, scales to 8+ cows). 013 has better robustness (evolved against strong opponents).
The hybrid might capture the best of both.
"""
import json, base64, zlib, copy

def load_trace(path):
    with open(path, 'r') as f:
        code = f.read()
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    return json.loads(zlib.decompress(base64.b85decode(code[q1+1:q2]))), code

def compress_actions(actions):
    compressed = zlib.compress(json.dumps(actions).encode('utf-8'))
    return base64.b85encode(compressed).decode('utf-8')

def save_trace(base_code, actions, output_path):
    b85 = compress_actions(actions)
    start = base_code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = base_code.find("'", start)
    q2 = base_code.find("'", q1 + 1)
    new_code = base_code[:q1+1] + b85 + base_code[q2:]
    with open(output_path, 'w') as f:
        f.write(new_code)
    print(f"Saved {output_path}")

# Load both traces
t013, code013 = load_trace('agents/013_robust_trace.py')
v092b, _ = load_trace('agents/v092b_replay_seed.py')

print(f"013 length: {len(t013)} steps")
print(f"v092b length: {len(v092b)} steps")

# Strategy 1: 013 Days 0-5, v092b Days 6-14, 013 Days 15-29
# Day boundaries: 24 steps/day
D0_5_end   = 6 * 24   # = 144
D6_14_end  = 15 * 24  # = 360
D15_end    = 30 * 24  # = 720

hybrid_a = copy.deepcopy(t013)
for i in range(D0_5_end, min(D6_14_end, len(v092b))):
    if i < len(hybrid_a) and i < len(v092b):
        # Only replace the MARKET actions (keep farm micro from 013)
        hybrid_a[i] = copy.deepcopy(v092b[i])

save_trace(code013, hybrid_a, 'agents/v094_hybrid_a.py')
print("Hybrid A: 013[0-5] + v092b[6-14] + 013[15+] (FULL replacement)")

# Strategy 2: Graft only the MARKET orders from v092b Days 6-14
hybrid_b = copy.deepcopy(t013)
for i in range(D0_5_end, min(D6_14_end, len(v092b))):
    if i < len(hybrid_b) and i < len(v092b):
        # Only inject market ops, keep farmer/hands from 013
        hybrid_b[i] = dict(hybrid_b[i])
        hybrid_b[i]['market'] = copy.deepcopy(v092b[i].get('market', []))

save_trace(code013, hybrid_b, 'agents/v094_hybrid_b.py')
print("Hybrid B: 013 farmer/hands + v092b market[6-14] (MARKET only injection)")

# Strategy 3: v092b Days 0-10, 013 Days 11-29
hybrid_c = copy.deepcopy(v092b)
for i in range(11 * 24, len(t013)):
    if i < len(hybrid_c):
        hybrid_c[i] = copy.deepcopy(t013[i])
    else:
        hybrid_c.append(copy.deepcopy(t013[i]))

save_trace(code013, hybrid_c, 'agents/v094_hybrid_c.py')
print("Hybrid C: v092b[0-10] + 013[11+]")
