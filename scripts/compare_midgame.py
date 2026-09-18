"""
Compare mid-game (Days 7-15) market actions between v057 winner and 013/014.
When v057 wins, what did it do differently in market timing?
"""
import json, base64, zlib

def load_trace(path):
    with open(path, 'r') as f:
        code = f.read()
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    return json.loads(zlib.decompress(base64.b85decode(code[q1+1:q2])))

v057 = load_trace('agents/v057_generalized_spoiler.py')
t013 = load_trace('agents/013_robust_trace.py')
t014 = load_trace('agents/014_robust_trace.py')

print("=== Days 7-15 market actions comparison ===\n")
for day in range(7, 16):
    print(f"--- Day {day} ---")
    for label, trace in [('v057', v057), ('013', t013), ('014', t014)]:
        day_actions = []
        for h in range(24):
            step = day * 24 + h
            if step >= len(trace): continue
            mkt = trace[step].get('market', [])
            if mkt:
                sells = [(op[1], op[2]) for op in mkt if op[0]=='SELL']
                hires = sum(1 for op in mkt if op[0]=='HIRE')
                animals = [op[1] for op in mkt if op[0]=='BUY_ANIMAL']
                land = sum(1 for op in mkt if op[0]=='BUY_LAND')
                seeds = {op[1]:op[2] for op in mkt if op[0]=='BUY_SEED'}
                if sells or hires or animals or land:
                    day_actions.append(f"H{h}: sells={sells} hires={hires} animals={animals} land={land} seeds={dict(seeds)}")
        if day_actions:
            print(f"  {label}:")
            for a in day_actions:
                print(f"    {a}")
    print()
