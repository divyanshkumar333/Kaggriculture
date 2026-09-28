import json
with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\replay_summary.json', 'r') as f:
    data = json.load(f)

for ep in data.get('V104_episodes', []):
    ep_id = ep['episode_id']
    try:
        with open(f'e:\\Setup\\kaggle\\kaggriculture\\RESEARCH\\kaggle_loop\\kaggle_forensics\\episode-{ep_id}-replay.json', 'r') as f2:
            replay = json.load(f2)
            
            m0 = str(ep['opening_markets'][0])
            m1 = str(ep['opening_markets'][1])
            is_p0 = '20' in m0 and '15' in m0
            is_p1 = '20' in m1 and '15' in m1
            p_idx = 0 if is_p0 else (1 if is_p1 else -1)
            if p_idx == -1: continue
            
            oscillation_count = 0
            for step in replay['steps'][2:25]:
                action = step[p_idx]['action']
                if action and 'market' in action:
                    mkt = action['market']
                    sells = sum(1 for o in mkt if o[0] == 'SELL' and o[1] == 'WHEAT')
                    buys = sum(1 for o in mkt if o[0] == 'BUY_PRODUCT' and o[1] == 'WHEAT')
                    if sells > 0 and buys > 0:
                        oscillation_count += 1
            if oscillation_count > 5:
                print(f'Episode {ep_id} had {oscillation_count} oscillating turns! V104 score: {ep["final_cash"][p_idx]}')
    except Exception as e:
        pass
