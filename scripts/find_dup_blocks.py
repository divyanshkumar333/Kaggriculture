"""Find duplicate commodity SELL blocks in 2945 farm V105"""
import sys
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')

from kaggle_environments import make
import importlib.util

spec = importlib.util.spec_from_file_location('v105', r'e:\Setup\kaggle\kaggriculture\agents\v105_revert_quote_priority.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make('kaggriculture', debug=False)
env.run([mod.agent, 'random'])

duplicate_blocks = []
for step_num, step in enumerate(env.steps):
    for player_idx, agent_state in enumerate(step):
        action = agent_state.get('action', {})
        if not action:
            continue
        market = action.get('market', [])
        if not market:
            continue
        sells = [o for o in market if isinstance(o, list) and len(o) >= 2 and o[0] == 'SELL']
        items = [o[1] for o in sells]
        if len(items) > 1 and len(items) != len(set(items)):
            duplicate_blocks.append({'step': step_num, 'player': player_idx, 'market': market})

print(f'Total duplicate sell-commodity blocks in game: {len(duplicate_blocks)}')
if duplicate_blocks:
    print('First 5:')
    for b in duplicate_blocks[:5]:
        print(f'  Step {b["step"]} P{b["player"]}: {b["market"]}')
    print('Last 5:')
    for b in duplicate_blocks[-5:]:
        print(f'  Step {b["step"]} P{b["player"]}: {b["market"]}')
