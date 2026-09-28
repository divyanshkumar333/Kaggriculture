import json
import glob
import os

def analyze_replay(filepath, us="Divyansh Kumar"):
    with open(filepath, 'r') as f:
        replay = json.load(f)
        
    if isinstance(replay, list):
        steps = replay
        info = {}
    else:
        steps = replay.get('steps', [])
        info = replay.get('info', {})
    team_names = info.get('TeamNames', [])
    our_idx = None
    opp_idx = None
    for i, name in enumerate(team_names):
        if name == us:
            our_idx = i
        else:
            opp_idx = i
            
    if our_idx is None:
        if len(team_names) > 0:
            if team_names[0] == us or team_names[1] == us:
                pass # impossible
            our_idx = 0
            opp_idx = 1
        else:
            our_idx = 0
            opp_idx = 1
            
    if opp_idx is None:
        opp_idx = 1 if our_idx == 0 else 0
        
    try:
        final_state = steps[-1][0]['observation']
        our_final_reward = steps[-1][our_idx]['reward'] or 0
        opp_final_reward = steps[-1][opp_idx]['reward'] or 0
    except KeyError:
        return None
    except TypeError:
        return None
    
    is_win = our_final_reward > opp_final_reward
    
    hands_over_time = []
    cash_over_time = []
    hire_events = []
    
    for step_idx, step in enumerate(steps):
        obs = step[0]['observation']
        if 'farms' not in obs:
            continue
            
        our_farm = obs['farms'][our_idx]
        hands = len(our_farm.get('hands', [])) + 1
        cash = our_farm.get('money', 0)
        
        hands_over_time.append(hands)
        cash_over_time.append(cash)
        
        if step_idx > 0:
            prev_obs = steps[step_idx-1][0]['observation']
            prev_hands = len(prev_obs['farms'][our_idx].get('hands', [])) + 1
            if hands > prev_hands:
                # Count the exact number of hands gained
                num_gained = hands - prev_hands
                for _ in range(num_gained):
                    hire_events.append(step_idx)
                
    turn_stops_scaling = hire_events[-1] if hire_events else 0
    max_hands = max(hands_over_time) if hands_over_time else 1
    
    # Calculate days with 0 hires
    days_with_0_hires = sum(1 for i in range(30) if hands_over_time[i*24 + 12] == 1)
    
    return {
        "file": os.path.basename(filepath),
        "win": is_win,
        "our_score": our_final_reward,
        "opp_score": opp_final_reward,
        "max_hands": max_hands,
        "days_with_0_hires": days_with_0_hires,
        "turn_stops_scaling": turn_stops_scaling,
        "hire_events": len(hire_events),
        "final_cash": cash_over_time[-1] if cash_over_time else 0
    }

if __name__ == '__main__':
    replays = glob.glob('kaggle_episodes/*.json')
    wins = []
    losses = []
    
    for r in replays:
        res = analyze_replay(r)
        if not res: continue
        if res["win"]:
            wins.append(res)
        else:
            losses.append(res)
            
    print(f"Total Wins: {len(wins)}, Total Losses: {len(losses)}")
    
    print("\n--- LOSSES ---")
    for l in sorted(losses, key=lambda x: x['our_score'])[:10]:
        print(f"{l['file']}: Score {l['our_score']} vs {l['opp_score']} | Max Hands {l['max_hands']} | Days 0 hires: {l['days_with_0_hires']} | Total Hires: {l['hire_events']}")
        
    print("\n--- WINS ---")
    for w in sorted(wins, key=lambda x: -x['our_score'])[:10]:
        print(f"{w['file']}: Score {w['our_score']} vs {w['opp_score']} | Max Hands {w['max_hands']} | Days 0 hires: {w['days_with_0_hires']} | Total Hires: {w['hire_events']}")

