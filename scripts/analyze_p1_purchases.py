import json
with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\episode-113341974-replay.json', 'r') as f:
    replay = json.load(f)

steps = replay['steps']
# Opponent is player 1
p_idx = 1
seeds = {'MELON':0, 'STRAWBERRY':0, 'TOMATO':0, 'CARROT':0, 'WHEAT':0}
animals = {'COW':0, 'SHEEP':0, 'GOOSE':0}

print('Analyzing P1 purchases...')
for step_idx, step in enumerate(steps):
    if step_idx == 0: continue
    action = step[p_idx].get('action')
    if action and 'market' in action:
        for o in action['market']:
            if o and len(o) >= 3:
                if o[0] == 'BUY_SEED':
                    crop = o[1]
                    qty = int(o[2])
                    if crop in seeds: seeds[crop] += qty
                elif o[0] == 'BUY_ANIMAL':
                    animal = o[1]
                    qty = int(o[2])
                    if animal in animals: animals[animal] += qty

print("P1 Total Purchases in episode 113341974:")
print(f"Seeds: {seeds}")
print(f"Animals: {animals}")
