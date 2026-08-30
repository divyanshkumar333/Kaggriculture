import json
import os
import glob
from collections import defaultdict

def analyze_all_replays(replay_dir='kaggle_episodes'):
    replays = sorted(glob.glob(os.path.join(replay_dir, '*-replay.json')))
    print(f'Found {len(replays)} replays to analyze.\n')
    
    summary_records = []
    
    for path in replays:
        fname = os.path.basename(path)
        with open(path, 'r') as f:
            data = json.load(f)
        
        steps = data['steps']
        total_steps = len(steps)
        if total_steps < 720:
            print(f'Skipping incomplete replay {fname} ({total_steps} steps)')
            continue
        
        final_step = steps[-1]
        p0_rew = final_step[0].get('reward', 0.0)
        p1_rew = final_step[1].get('reward', 0.0)
        p0_win = p0_rew > p1_rew
        p1_win = p1_rew > p0_rew
        
        # Track timeline statistics
        p0_max_hands = 0
        p1_max_hands = 0
        p0_animals_timeline = defaultdict(int)
        p1_animals_timeline = defaultdict(int)
        p0_crops_planted_total = defaultdict(int)
        p1_crops_planted_total = defaultdict(int)
        p0_max_quads = 1
        p1_max_quads = 1
        
        # Analyze day-by-day
        for day in range(30):
            step_idx = day * 24 + 1
            if step_idx >= total_steps:
                step_idx = total_steps - 1
            obs = steps[step_idx][0]['observation']
            f0 = obs['farms'][0]
            f1 = obs['farms'][1]
            
            p0_max_hands = max(p0_max_hands, len(f0['hands']))
            p1_max_hands = max(p1_max_hands, len(f1['hands']))
            p0_max_quads = max(p0_max_quads, len(f0.get('unlocked_quadrants', [])))
            p1_max_quads = max(p1_max_quads, len(f1.get('unlocked_quadrants', [])))
            
            for row in f0['tiles']:
                for t in row:
                    if isinstance(t, dict) and t.get('animal'):
                        p0_animals_timeline[t['animal']] = max(p0_animals_timeline[t['animal']], 1)
            for row in f1['tiles']:
                for t in row:
                    if isinstance(t, dict) and t.get('animal'):
                        p1_animals_timeline[t['animal']] = max(p1_animals_timeline[t['animal']], 1)
        
        # Check action steps for total seeds planted
        for step in steps:
            # Action is in step[0]['action'] and step[1]['action']
            for p_idx, p_crops in [(0, p0_crops_planted_total), (1, p1_crops_planted_total)]:
                action = step[p_idx].get('action')
                if isinstance(action, dict):
                    # farmer action
                    farmer_act = action.get('farmer')
                    if isinstance(farmer_act, list) and len(farmer_act) >= 2 and farmer_act[0] == 'PLANT':
                        p_crops[farmer_act[1]] += 1
                    # hands actions
                    for hand_act in action.get('hands', []):
                        if isinstance(hand_act, list) and len(hand_act) >= 2 and hand_act[0] == 'PLANT':
                            p_crops[hand_act[1]] += 1
        
        rec = {
            'file': fname,
            'p0_rew': p0_rew,
            'p1_rew': p1_rew,
            'winner': 'P0 (Us)' if p0_win else 'P1 (Opponent)' if p1_win else 'Tie',
            'p0_max_hands': p0_max_hands,
            'p1_max_hands': p1_max_hands,
            'p0_max_quads': p0_max_quads,
            'p1_max_quads': p1_max_quads,
            'p0_animals': dict(p0_animals_timeline),
            'p1_animals': dict(p1_animals_timeline),
            'p0_crops': dict(p0_crops_planted_total),
            'p1_crops': dict(p1_crops_planted_total)
        }
        summary_records.append(rec)
        
        print(f"=== {fname} ===")
        print(f"Result: P0 = {p0_rew:8.0f} vs P1 = {p1_rew:8.0f} -> Winner: {rec['winner']}")
        print(f"P0: max_hands={p0_max_hands}, quads={p0_max_quads}, animals={rec['p0_animals']}, crops_planted={rec['p0_crops']}")
        print(f"P1: max_hands={p1_max_hands}, quads={p1_max_quads}, animals={rec['p1_animals']}, crops_planted={rec['p1_crops']}")
        print("-" * 80)

    # Aggregate stats
    total_games = len(summary_records)
    p0_wins = sum(1 for r in summary_records if r['p0_rew'] > r['p1_rew'])
    print(f"\n==================== AGGREGATE REAL KAGGLE STATS ({total_games} GAMES) ====================")
    print(f"Our Win Rate: {p0_wins}/{total_games} ({p0_wins/total_games*100:.1f}%)")
    print(f"Our Mean Bank: ${sum(r['p0_rew'] for r in summary_records)/total_games:,.0f}")
    print(f"Opponent Mean Bank: ${sum(r['p1_rew'] for r in summary_records)/total_games:,.0f}")
    
    # Analyze what opponents did when they beat us
    opp_wins = [r for r in summary_records if r['p1_rew'] > r['p0_rew']]
    print(f"\nIn {len(opp_wins)} games where OPPONENT WON:")
    for r in opp_wins:
        print(f"  {r['file']}: Opp earned ${r['p1_rew']:,.0f} vs our ${r['p0_rew']:,.0f} | Hands: {r['p1_max_hands']} | Quads: {r['p1_max_quads']} | Animals: {r['p1_animals']} | Crops: {r['p1_crops']}")

if __name__ == '__main__':
    analyze_all_replays()
