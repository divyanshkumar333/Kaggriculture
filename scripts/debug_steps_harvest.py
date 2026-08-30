from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 200}, debug=False)
agent_b = load_agent("agents/v019_b_market_adaptive.py")
agent_a = load_agent("agents/v019_a_control.py")

for step_idx in range(350):
    obs = env.state[0].observation
    action_b = agent_b(obs)
    action_a = agent_a(env.state[1].observation)
    env.step([action_b, action_a])
    if 240 <= step_idx <= 300 and step_idx % 4 == 0:
        p0_farm = env.state[0].observation.farms[0]
        p1_farm = env.state[0].observation.farms[1]
        p0_shed = env.state[0].observation.private.get("shed", {})
        p1_shed = env.state[1].observation.private.get("shed", {})
        print(f"Step {step_idx:3d} (Day {step_idx//24:2d}, Hr {step_idx%24:2d}):")
        print(f"  P0 ($ {p0_farm['money']:6.0f}, shed: {p0_shed}): {action_b}")
        print(f"  P1 ($ {p1_farm['money']:6.0f}, shed: {p1_shed}): {action_a}")
