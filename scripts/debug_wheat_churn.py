import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"mod_{abs(hash(filepath))}", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

# Test seed 404 with wheat sell churn fixed
env = make("kaggriculture", configuration={"episodeSteps": 24*6, "seed": 404}, debug=False)
for step in range(24*6):
    obs = env.state[0].observation
    # Let's inspect wheat in shed and market orders
    if step % 24 == 0:
        d = step // 24
        print(f"Day {d} Start: Shed Wheat = {obs['private']['shed'].get('WHEAT', 0)}")
    env.step([a_v025(env.state[0].observation), a_v025(env.state[1].observation)])
