"""
Analyze the 5-COW opening opponent from episode 110446993 (our biggest loss, -29k).
Extract their full 720-step trace and see if we can use it as a new seed.
"""
import json, base64, zlib, os

def compress_trace(actions):
    compressed = zlib.compress(json.dumps(actions).encode('utf-8'))
    return base64.b85encode(compressed).decode('utf-8')

def load_code_template(agent_path):
    with open(agent_path, 'r') as f:
        return f.read()

def load_trace(path):
    with open(path, 'r') as f:
        code = f.read()
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    return json.loads(zlib.decompress(base64.b85decode(code[q1+1:q2]))), code

def save_trace_from_replay(replay_player_idx, replay_path, output_path, template_path):
    """Extract player's actions from a replay and save as agent file."""
    with open(replay_path) as f:
        data = json.load(f)
    
    steps = data['steps']
    actions = []
    for step in steps[1:]:  # step 0 is initial obs, step 1+ has actions
        player_step = step[replay_player_idx]
        action = player_step.get('action') or {}
        # Convert to the format our agents use
        actions.append({
            'farmer': action.get('farmer', ['PASS']),
            'hands': action.get('hands', []),
            'market': action.get('market', []),
        })
    
    # Pad to 720 if needed
    while len(actions) < 720:
        actions.append({'farmer': ['PASS'], 'hands': [], 'market': []})
    actions = actions[:720]
    
    # Load template code and inject actions
    code = load_code_template(template_path)
    b85 = compress_trace(actions)
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    new_code = code[:q1+1] + b85 + code[q2:]
    
    with open(output_path, 'w') as f:
        f.write(new_code)
    
    return actions

# Episode 110446993: we were P1 (idx=1), opponent was P0 (idx=0)
# Opponent scored 88k vs our 58k - they beat us by 29k
ep_path = 'replays/episode-110446993-replay.json'

print("Extracting 5-COW opening opponent's trace...")
actions = save_trace_from_replay(0, ep_path, 'agents/v095_5cow_opening.py', 'agents/013_robust_trace.py')

# Show first 48 steps
print(f"\nExtracted {len(actions)} steps")
print("\n=== Day 0-1 actions ===")
for i, a in enumerate(actions[:48]):
    day = i // 24
    hour = i % 24
    farmer = a.get('farmer', ['PASS'])
    market = a.get('market', [])
    hands = [h for h in a.get('hands', []) if h and h != ['PASS']]
    if market or farmer != ['PASS'] or hands:
        print(f"  D{day}H{hour}: farmer={farmer} hands={hands[:2]} market={market}")

# Show income analysis
print("\n=== Days 0-8 market summary ===")
for day in range(9):
    sells = []
    animals = []
    hires = 0
    seeds = {}
    for h in range(24):
        step = day*24+h
        if step >= len(actions): break
        m = actions[step].get('market', [])
        for op in m:
            if op[0]=='SELL': sells.append((op[1], op[2] if len(op)>2 else 1))
            elif op[0]=='BUY_ANIMAL': animals.append(op[1])
            elif op[0]=='HIRE': hires += 1
            elif op[0]=='BUY_SEED': seeds[op[1]] = seeds.get(op[1],0) + op[2]
    if sells or animals or hires:
        print(f"  Day {day}: hires={hires} animals={animals} sells={sells[:4]} seeds={seeds}")
