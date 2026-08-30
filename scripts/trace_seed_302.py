from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 302}, debug=True)
agent_c = load_agent("agents/v020_c_competitive_surgical.py")
agent_a = load_agent("agents/v020_a_control.py")

for step in range(720):
    obs_c = env.state[0].observation
    obs_a = env.state[1].observation
    act_c = agent_c(obs_c)
    act_a = agent_a(obs_a)
    env.step([act_c, act_a])
    if step % 48 == 0 or step in [715, 716, 717, 718, 719]:
        f0 = env.state[0].observation.farms[0]
        f1 = env.state[1].observation.farms[1]
        p0 = env.state[0].observation.private
        p1 = env.state[1].observation.private
        print(f"Step {step:3d} (Day {step//24:2d}, Hr {step%24:2d}) | P0 (V020-C): ${f0['money']:5.0f} (quads: {len(f0['unlocked_quadrants'])}) | P1 (V020-A): ${f1['money']:5.0f} (quads: {len(f1['unlocked_quadrants'])})")
