import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("mod", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

a_v026 = load_agent("agents/v026_il_meta.py")
a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 101}, debug=False)
for step in range(720):
    obs0 = env.state[0].observation
    act0 = a_v026(obs0)
    act1 = a_v025(env.state[1].observation)
    env.step([act0, act1])
    if step in [24*15, 24*20, 24*25, 719]:
        d = step // 24
        f0 = env.state[0].observation.farms[0]
        f1 = env.state[0].observation.farms[1]
        p0 = env.state[0].observation.private if hasattr(env.state[0].observation, 'private') else {}
        print(f"\n--- DAY {d} ---")
        print(f"V026: Money=${f0['money']:,.0f}, Hires={f0.get('hires_today', 0)}, Quads={f0['unlocked_quadrants']}")
        print(f"V025: Money=${f1['money']:,.0f}, Hires={f1.get('hires_today', 0)}, Quads={f1['unlocked_quadrants']}")
        # count plants and animals
        c0, s0, straw0, w0 = 0, 0, 0, 0
        for row in f0['tiles']:
            for t in row:
                if isinstance(t, dict):
                    k = t.get('kind')
                    if k == 'PASTURE':
                        an = t.get('animal')
                        if an == 'COW': c0 += 1
                        elif an == 'SHEEP': s0 += 1
                    elif k == 'PLANT':
                        cr = t.get('crop')
                        if cr == 'STRAWBERRY': straw0 += 1
                        elif cr == 'WHEAT': w0 += 1
                        
        c1, s1, straw1, w1 = 0, 0, 0, 0
        for row in f1['tiles']:
            for t in row:
                if isinstance(t, dict):
                    k = t.get('kind')
                    if k == 'PASTURE':
                        an = t.get('animal')
                        if an == 'COW': c1 += 1
                        elif an == 'SHEEP': s1 += 1
                    elif k == 'PLANT':
                        cr = t.get('crop')
                        if cr == 'STRAWBERRY': straw1 += 1
                        elif cr == 'WHEAT': w1 += 1
        print(f"V026 Board: Cows={c0}, Sheep={s0}, Strawberries={straw0}, Wheat={w0}")
        print(f"V025 Board: Cows={c1}, Sheep={s1}, Strawberries={straw1}, Wheat={w1}")
