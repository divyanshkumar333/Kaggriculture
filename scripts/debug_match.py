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

print("Running single match...")
env.run([agent_b, agent_a])

for step_idx, step in enumerate(env.steps):
    if step_idx % 48 == 0 or step_idx == 719:
        p0_farm = step[0].observation.farms[0]
        p1_farm = step[0].observation.farms[1]
        market = step[0].observation.market
        action0 = step[0].action
        print(f"Step {step_idx:3d} (Day {step_idx//24:2d}) | P0 Money: ${p0_farm['money']:6.0f} | P1 Money: ${p1_farm['money']:6.0f} | Melon Price: ${market['prices'].get('MELON', 0)} | Carrot Price: ${market['prices'].get('CARROT', 0)} | Action0: {action0}")
