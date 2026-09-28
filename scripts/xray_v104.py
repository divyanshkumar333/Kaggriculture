import json
import glob
from pathlib import Path

def analyze_replay(filepath):
    print(f"\n{'='*60}")
    print(f"Analyzing {filepath}")
    with open(filepath, 'r') as f:
        replay = json.load(f)
        
    steps = replay['steps']
    num_steps = len(steps)
    
    info = replay.get('info', {})
    teams = info.get('TeamNames', ["Player 0", "Player 1"])
    print(f"Teams: {teams[0]} vs {teams[1]}")
    
    rewards = [steps[-1][0]['reward'], steps[-1][1]['reward']]
    print(f"Final Score: P0 {rewards[0]} vs P1 {rewards[1]}")
    winner = 0 if rewards[0] > rewards[1] else 1
    
    divyansh_idx = 0 if "Divyansh Kumar" in teams[0] else 1
    if "Divyansh Kumar" not in teams[0] and "Divyansh Kumar" not in teams[1]:
        divyansh_idx = 0 # Default if we don't know
        
    print(f"Our Agent is P{divyansh_idx}")
    print(f"Result: {'WIN' if divyansh_idx == winner else 'LOSS'}")
    
    trajectories = [[], []]
    market_orders = [[], []]
    
    for step_idx, step in enumerate(steps):
        # Extract actions (market orders)
        if step_idx > 0:
            for p in (0, 1):
                action = step[p].get('action', {})
                if action and 'market' in action:
                    orders = action['market']
                    if orders:
                        market_orders[p].append({'step': step_idx, 'orders': orders})
        
        obs = step[0]['observation']
        if 'farms' not in obs:
            continue
            
        for p in (0, 1):
            farm = obs['farms'][p]
            money = farm['money']
            
            workers = 1 + len(farm.get('hands', []))
            
            cows, sheep, geese = 0, 0, 0
            tiles = farm.get('tiles', [])
            for row in tiles:
                for tile in row:
                    if isinstance(tile, dict):
                        if tile.get('kind') == 'PASTURE':
                            if tile.get('animal') == 'COW': cows += 1
                            elif tile.get('animal') == 'SHEEP': sheep += 1
                        elif tile.get('kind') == 'COOP':
                            if tile.get('animal') == 'GOOSE': geese += 1
                            
            trajectories[p].append({
                'step': step_idx,
                'money': money,
                'workers': workers,
                'cows': cows,
                'sheep': sheep,
                'geese': geese
            })
            
    # Find divergences
    for p in (0, 1):
        max_cows = max(t['cows'] for t in trajectories[p]) if trajectories[p] else 0
        max_sheep = max(t['sheep'] for t in trajectories[p]) if trajectories[p] else 0
        max_workers = max(t['workers'] for t in trajectories[p]) if trajectories[p] else 0
        print(f"P{p} ({teams[p][:10]}...): Route -> {max_workers}W, {max_cows}C, {max_sheep}S")

    # Find when cash starts heavily diverging
    cash_diff = []
    first_major_divergence = None
    for t0, t1 in zip(trajectories[0], trajectories[1]):
        diff = t0['money'] - t1['money']
        cash_diff.append(diff)
        if first_major_divergence is None and abs(diff) > 2000:
            first_major_divergence = t0['step']
            
    print(f"First major cash divergence (>2000): Step {first_major_divergence}")
    
    # Let's inspect early market orders (e.g. first 5 turns of market orders)
    print("Early Market Orders P0:")
    for m in market_orders[0][:3]: print(f"  Step {m['step']}: {m['orders']}")
    print("Early Market Orders P1:")
    for m in market_orders[1][:3]: print(f"  Step {m['step']}: {m['orders']}")

if __name__ == '__main__':
    replays_dir = Path("RESEARCH/kaggle_loop/kaggle_forensics/v104/replays")
    for filepath in list(replays_dir.glob("*.json"))[:6]:
        analyze_replay(filepath)
