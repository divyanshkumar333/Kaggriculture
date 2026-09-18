"""
Analyze what v057 is doing to earn 124k+ while v090 only earns 24k.
Look at late-game money flow, market prices, and what's being sold.
"""
from kaggle_environments import make

env = make('kaggriculture', configuration={'episodeSteps': 720}, debug=False)
env.run(['agents/v090_meta_adaptive.py', 'agents/v057_generalized_spoiler.py'])

# Analyze every day at hour 0
for step_idx, step in enumerate(env.steps):
    obs = step[0]['observation']
    day = obs['day']
    hour = obs['hour']
    if hour != 0: continue
    
    m0 = obs['farms'][0]['money']
    m1 = obs['farms'][1]['money']
    tiles0 = obs['farms'][0]['tiles']
    tiles1 = obs['farms'][1]['tiles']
    
    an0 = sum(1 for row in tiles0 for t in row if isinstance(t, dict) and t.get('animal'))
    an1 = sum(1 for row in tiles1 for t in row if isinstance(t, dict) and t.get('animal'))
    pl0 = sum(1 for row in tiles0 for t in row if isinstance(t, dict) and t.get('kind') == 'PLANT')
    pl1 = sum(1 for row in tiles1 for t in row if isinstance(t, dict) and t.get('kind') == 'PLANT')
    
    mkt = obs['market']
    fert_price = mkt['prices'].get('FERTILIZER', 100)
    milk_price = mkt['prices'].get('MILK', 150)
    wool_price = mkt['prices'].get('WOOL', 200)
    wheat_price = mkt['prices'].get('WHEAT', 25)
    
    print(f"D{day}: P0=${m0:.0f}(an={an0},pl={pl0}) vs P1=${m1:.0f}(an={an1},pl={pl1}) | fert=${fert_price} milk=${milk_price} wool=${wool_price} wheat=${wheat_price}")
