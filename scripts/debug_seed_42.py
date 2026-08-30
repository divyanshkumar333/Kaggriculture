from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
agent_c = load_agent("agents/v020_c_competitive_surgical.py")

for step in range(720):
    obs = env.state[0].observation
    act = agent_c(obs)
    env.step([act, "random"])
    if step % 24 == 0 or step in [10, 20, 30, 40, 50]:
        f = env.state[0].observation.farms[0]
        p = env.state[0].observation.private
        m = env.state[0].observation.market
        print(f"Step {step:3d} (Day {step//24:2d}, Hr {step%24:2d}) | Money: ${f['money']:5.0f} | Seeds: {p.get('seeds')} | Shed: {p.get('shed')} | Act: {act}")
