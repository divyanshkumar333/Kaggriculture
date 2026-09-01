import json

with open('kaggle_episodes/episode-103388734-replay.json', 'r') as f:
    data = json.load(f)
steps = data['steps']
for day in range(8):
    day_steps = steps[day*24:(day+1)*24]
    p_start = day_steps[0][0]['observation']['farms'][1]
    p_end = day_steps[-1][0]['observation']['farms'][1]
    
    buys, sells, plants, builds, places = {}, {}, {}, {}, {}
    for s in day_steps:
        act = s[1].get('action', {})
        for o in act.get('market', []):
            if o[0] == 'SELL': sells[o[1]] = sells.get(o[1], 0) + o[2]
            elif o[0] in ['BUY_SEED', 'BUY_PRODUCT', 'BUY_ANIMAL']: buys[f"{o[0]}_{o[1]}"] = buys.get(f"{o[0]}_{o[1]}", 0) + o[2]
            elif o[0] in ['BUY_LAND', 'HIRE']: buys[o[0]] = buys.get(o[0], 0) + 1
        all_u = [act.get('farmer', [])] + act.get('hands', [])
        for u in all_u:
            if not u: continue
            if u[0] == 'PLANT': plants[u[1]] = plants.get(u[1], 0) + 1
            elif u[0] in ['BUILD_PASTURE', 'BUILD_COOP']: builds[u[0]] = builds.get(u[0], 0) + 1
            elif u[0] == 'PLACE': places[u[1]] = places.get(u[1], 0) + 1
            
    m_s = p_start["money"]
    m_e = p_end["money"]
    q = len(p_end["unlocked_quadrants"])
    h = len(p_end["hands"])
    print(f"Day {day:2d} | Money: ${m_s:,.0f} -> ${m_e:,.0f} | Quads: {q} | Hands: {h}")
    print(f"   BUYS:   {buys}")
    print(f"   SELLS:  {sells}")
    print(f"   PLANTS: {plants}")
    print(f"   BUILDS: {builds}")
    print(f"   PLACES: {places}")
