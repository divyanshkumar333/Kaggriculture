import json
import os

def trace_replay(path):
    print("================================================================================")
    print("TRACING REPLAY:", os.path.basename(path))
    with open(path, 'r') as f:
        data = json.load(f)
    
    steps = data['steps']
    final_step = steps[-1]
    p0_rew = final_step[0].get('reward', 0)
    p1_rew = final_step[1].get('reward', 0)
    print(f"Final Score: P0 = ${p0_rew:,.0f} | P1 = ${p1_rew:,.0f}")
    
    # Identify which player was the livestock player
    # We inspect day 15 state
    obs15 = steps[15 * 24 + 1][0]['observation']
    f0_animals = sum(1 for r in obs15['farms'][0]['tiles'] for t in r if isinstance(t, dict) and t.get('animal'))
    f1_animals = sum(1 for r in obs15['farms'][1]['tiles'] for t in r if isinstance(t, dict) and t.get('animal'))
    
    livestock_player = 1 if f1_animals > f0_animals else 0
    print(f"Livestock Player is: P{livestock_player} (Animals on Day 15: {max(f0_animals, f1_animals)})")
    
    print("\nDAY-BY-DAY TIMELINE OF LIVESTOCK PLAYER:")
    print("Day | Bank    | Hands | Quads | Pastures | Coops | Cows | Sheep | Geese | Wheat | Mel/Str | Feed In Shed | Milk In Shed | Orders Executed")
    print("-" * 135)
    
    for day in range(30):
        step_idx = day * 24 + 1
        if step_idx >= len(steps): step_idx = len(steps) - 1
        obs = steps[step_idx][0]['observation']
        farm = obs['farms'][livestock_player]
        priv = steps[step_idx][livestock_player].get('observation', {}).get('private', {})
        # Note: in replay JSON, step[p]['observation']['private'] might only exist for player p if not sanitized, or in step 0
        shed = farm.get('shed', {}) # if visible or from state
        
        # Count tiles
        pastures = 0
        coops = 0
        cows = 0
        sheep = 0
        geese = 0
        wheat = 0
        mel_str = 0
        
        for r in farm['tiles']:
            for t in r:
                if isinstance(t, dict):
                    kind = t.get('kind')
                    if kind == 'PASTURE':
                        pastures += 1
                        if t.get('animal') == 'COW': cows += 1
                        elif t.get('animal') == 'SHEEP': sheep += 1
                    elif kind == 'COOP':
                        coops += 1
                        if t.get('animal') == 'GOOSE': geese += 1
                    elif kind == 'PLANT':
                        c = t.get('crop')
                        if c == 'WHEAT': wheat += 1
                        elif c in ['MELON', 'STRAWBERRY']: mel_str += 1
                        
        # Collect market actions across the day
        day_market_ops = []
        for h in range(24):
            s_idx = day * 24 + h
            if s_idx < len(steps):
                act = steps[s_idx][livestock_player].get('action')
                if isinstance(act, dict):
                    for m_op in act.get('market', []):
                        day_market_ops.append(m_op[0])
                        
        op_counts = {}
        for op in day_market_ops:
            op_counts[op] = op_counts.get(op, 0) + 1
            
        hands_cnt = len(farm.get('hands', []))
        quads_cnt = len(farm.get('unlocked_quadrants', []))
        money = farm.get('money', 0)
        
        print(f"{day:3d} | ${money:7,.0f} | {hands_cnt:5d} | {quads_cnt:5d} | {pastures:8d} | {coops:5d} | {cows:4d} | {sheep:5d} | {geese:5d} | {wheat:5d} | {mel_str:7d} | {'--':12s} | {'--':12s} | {dict(op_counts)}")

if __name__ == '__main__':
    replays = [
        'kaggle_episodes/episode-103388734-replay.json',
        'kaggle_episodes/episode-103533735-replay.json',
        'kaggle_episodes/episode-103527222-replay.json',
        'kaggle_episodes/episode-103500320-replay.json'
    ]
    for r in replays:
        if os.path.exists(r):
            trace_replay(r)
