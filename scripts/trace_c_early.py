from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
agent_c = load_agent("agents/v020_c_competitive_surgical.py")

for step in range(120):
    obs = env.state[0].observation
    act = agent_c(obs)
    env.step([act, "random"])
    if step % 8 == 0:
        f = env.state[0].observation.farms[0]
        p = env.state[0].observation.private
        m = env.state[0].observation.market
        print(f"Step {step:3d} (Day {step//24:2d}, Hr {step%24:2d}) | Money: ${f['money']:5.0f} | Hands: {len(f['hands'])} | Seeds: {p.get('seeds')} | Act: {act}")
