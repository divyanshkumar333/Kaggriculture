import json
with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\episode-113341974-replay.json', 'r') as f:
    replay = json.load(f)

p1_idx = 1
print("P1 actions Day 0 (steps 0-23):")
for i in range(1, 24):
    print(f"Step {i}: {replay['steps'][i][p1_idx].get('action', {})}")
