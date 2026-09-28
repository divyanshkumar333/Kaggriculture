"""
Deep analysis of a V105 crushing loss episode.
Who is the opponent? What strategy? Why did they score 158k vs V105's 54k?
"""
import json, sys
from pathlib import Path

def analyze_replay(replay_path, our_player=0):
    data = json.loads(Path(replay_path).read_text(encoding='utf-8'))
    steps = data.get('steps', [])
    
    print(f"=== EPISODE ANALYSIS: {replay_path} ===")
    print(f"Total steps: {len(steps)}")
    
    final = steps[-1]
    rewards = [s.get('reward') for s in final]
    print(f"Final rewards: P0={rewards[0]:.0f}  P1={rewards[1]:.0f}")
    winner = 0 if rewards[0] > rewards[1] else 1
    loser = 1 - winner
    print(f"Winner: P{winner} (us: P{our_player})")
    
    # Analyze winner strategy
    print(f"\n=== WINNER (P{winner}) STRATEGY ===")
    
    # Track market orders across key time windows
    day_market_summary = {}
    for step_num, step in enumerate(steps):
        day = step_num // 24
        if winner < len(step):
            action = step[winner].get('action', {})
            if not action:
                continue
            market = action.get('market', [])
            if market:
                if day not in day_market_summary:
                    day_market_summary[day] = []
                day_market_summary[day].extend(market)
    
    # Opening (Day 0-2): what seeds/animals did winner buy?
    print("\nOpening buys (Days 0-3):")
    opening_buys = set()
    for day in range(4):
        if day in day_market_summary:
            for order in day_market_summary[day]:
                if isinstance(order, list) and order and order[0] in ('BUY_SEED', 'BUY_ANIMAL', 'BUY_LAND'):
                    opening_buys.add(tuple(order))
                    print(f"  Day {day}: {order}")
    
    # Main strategy: check tiles at midgame
    mid_step = 360  # Day 15
    if mid_step < len(steps):
        mid_obs = steps[mid_step][winner].get('observation', {})
        farms = mid_obs.get('farms', [])
        if winner < len(farms):
            farm = farms[winner]
            tiles = farm.get('tiles', [])
            money = farm.get('money', 0)
            print(f"\nMidgame (Day 15):")
            print(f"  Cash: {money:.0f}")
            
            # Count tile types
            plants = {}
            animals = {}
            empty = 0
            for row in tiles:
                for tile in row:
                    if tile is None:
                        empty += 1
                    elif isinstance(tile, dict):
                        kind = tile.get('kind', '?')
                        if kind == 'PLANT':
                            crop = tile.get('crop', '?')
                            plants[crop] = plants.get(crop, 0) + 1
                        elif kind in ('COOP', 'PASTURE'):
                            animal = tile.get('animal', 'empty')
                            animals[animal] = animals.get(animal, 0) + 1
                        elif kind == 'WEED':
                            empty += 1
            
            print(f"  Plants: {dict(plants)}")
            print(f"  Animals: {dict(animals)}")
            print(f"  Empty/weed: {empty}")
    
    # Selling pattern: what did winner sell most?
    sell_totals = {}
    for day, orders in day_market_summary.items():
        for order in orders:
            if isinstance(order, list) and order and order[0] == 'SELL':
                item = order[1] if len(order) > 1 else '?'
                qty = order[2] if len(order) > 2 else 1
                sell_totals[item] = sell_totals.get(item, 0) + qty
    
    print(f"\nTotal sell volumes (winner):")
    for item, qty in sorted(sell_totals.items(), key=lambda x: -x[1]):
        print(f"  {item}: {qty}")
    
    # Endgame cash trajectory
    print(f"\nEndgame cash trajectory (winner P{winner}):")
    for day in range(25, 30):
        step_num = day * 24
        if step_num < len(steps):
            obs = steps[step_num][winner].get('observation', {})
            farms = obs.get('farms', [])
            if winner < len(farms):
                print(f"  Day {day}: {farms[winner].get('money', 0):.0f}")
    
    print(f"\nEndgame cash trajectory (V105 P{our_player}):")
    for day in range(25, 30):
        step_num = day * 24
        if step_num < len(steps):
            obs = steps[step_num][our_player].get('observation', {})
            farms = obs.get('farms', [])
            if our_player < len(farms):
                print(f"  Day {day}: {farms[our_player].get('money', 0):.0f}")

analyze_replay(r'RESEARCH\kaggle_loop\kaggle_forensics\episode-113341974-replay.json', our_player=0)
print()
analyze_replay(r'RESEARCH\kaggle_loop\kaggle_forensics\episode-113344258-replay.json', our_player=0)
