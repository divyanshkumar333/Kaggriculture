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

for step_idx in range(50):
    obs = env.state[0].observation
    action_b = agent_b(obs)
    action_a = agent_a(env.state[1].observation)
    env.step([action_b, action_a])
    if step_idx < 10:
        print(f"Step {step_idx}:")
        print(f"  P0 money: {env.state[0].observation.farms[0]['money']}, P0 action: {action_b}")
        print(f"  P1 money: {env.state[0].observation.farms[1]['money']}, P1 action: {action_a}")
