import json
import base64
import zlib
import os

def extract_tape(replay_path, player_index):
    print(f"Extracting tape from {os.path.basename(replay_path)} for Player {player_index}...")
    with open(replay_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    steps = data.get("steps", [])
    if not steps:
        raise ValueError("No steps found in replay")
        
    extracted_tape = []
    
    # Kaggle replay step 0 is initial observation, step 1 is first actions
    # Actions correspond to steps 1..720. 
    for step_idx in range(1, len(steps)):
        step = steps[step_idx]
        player_step = step[player_index]
        action = player_step.get("action", {})
        
        # We only want the physical actions
        farmer_act = action.get("farmer", ["PASS"])
        hands_act = action.get("hands", [])
        
        extracted_tape.append({
            "farmer": farmer_act,
            "hands": hands_act
        })
        
    # Pad to 720 just in case
    while len(extracted_tape) < 720:
        extracted_tape.append({"farmer": ["PASS"], "hands": []})
        
    print(f"Extracted {len(extracted_tape)} steps.")
    
    # Compress it
    dumped = json.dumps(extracted_tape, separators=(',', ':')).encode('utf-8')
    compressed = zlib.compress(dumped, level=9)
    encoded = base64.b85encode(compressed).decode('ascii')
    
    # Save it to a python file
    out_code = f"""import json, base64, zlib
_TAPE = json.loads(zlib.decompress(base64.b85decode('{encoded}')))
def agent(obs):
    step = obs["step"]
    if step < len(_TAPE):
        return _TAPE[step]
    return {{"farmer": ["PASS"], "hands": [], "market": []}}
"""
    with open("agents/extracted_162k_route.py", "w", encoding="utf-8") as f:
        f.write(out_code)
    print("Saved to agents/extracted_162k_route.py")
    
    # Also save the raw array for easy debugging
    with open("agents/extracted_162k_raw.json", "w", encoding="utf-8") as f:
        json.dump(extracted_tape, f, indent=2)

if __name__ == "__main__":
    extract_tape(r"e:\Setup\kaggle\kaggriculture\kaggle_episodes\episode-103388734-replay.json", 1)
