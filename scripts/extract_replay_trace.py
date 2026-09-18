"""
Extract the winner's raw actions from a top replay JSON
and save them as a standalone agent file in the same format as 013_robust_trace.py
"""
import json
import base64
import zlib
import sys

def main(replay_path, output_path):
    with open(replay_path, 'r') as f:
        data = json.load(f)
    
    steps = data['steps']
    final_p0 = steps[-1][0]['reward']
    final_p1 = steps[-1][1]['reward']
    winner = 0 if final_p0 >= final_p1 else 1
    
    print(f"Replay: {replay_path}")
    print(f"Winner: P{winner} with ${max(final_p0, final_p1):.0f}")
    
    # Extract all actions from the winner
    actions = []
    for step_idx, step in enumerate(steps):
        action = step[winner].get('action') or {}
        # Normalize to ensure all required fields
        clean = {
            "farmer": list(action.get("farmer") or ["PASS"]),
            "hands": [list(h) for h in (action.get("hands") or [])],
            "market": [list(op) for op in (action.get("market") or [])]
        }
        actions.append(clean)
    
    print(f"Extracted {len(actions)} action steps")
    
    # Compress and encode
    compressed = zlib.compress(json.dumps(actions).encode('utf-8'))
    b85_str = base64.b85encode(compressed).decode('utf-8')
    
    # Write as standalone agent
    code = f'''"""
Replay-derived agent from top Kaggle game (winner score: {max(final_p0, final_p1):.0f}).
Extracted as trace for use as evolution seed.
"""
import json, base64, zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    \'{b85_str}\'
)))

def agent(obs):
    step = obs.get("step", 0)
    action = _ACTIONS[min(step, len(_ACTIONS) - 1)]
    hands = obs.get("farms", [{{}}])[obs.get("player", 0)].get("hands", [])
    hand_actions = action.get("hands", [])
    while len(hand_actions) < len(hands):
        hand_actions.append(["PASS"])
    return {{
        "farmer": action.get("farmer", ["PASS"]),
        "hands": hand_actions[:len(hands)],
        "market": action.get("market", [])
    }}
'''
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main("episode-110135509-replay.json", "agents/v092_replay_seed.py")
