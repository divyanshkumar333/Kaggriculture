from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 100}, debug=False)
agent_a = load_agent("agents/v020_a_control.py")
agent_opp = load_agent("agents/v005_d_combined.py")

for step_idx in range(720):
    obs_a = env.state[0].observation
    obs_opp = env.state[1].observation
    act_a = agent_a(obs_a)
    act_opp = agent_opp(obs_opp)
    env.step([act_a, act_opp])
    if step_idx % 48 == 0 or step_idx == 719:
        p0 = env.state[0].observation.farms[0]
        p1 = env.state[1].observation.farms[1]
        market = env.state[0].observation.market
        print(f"Step {step_idx:3d} (Day {step_idx//24:2d}): P0 (Control) Money: ${p0['money']:6.0f} | P1 (V005-D Animal) Money: ${p1['money']:6.0f} | Melon Price: ${market['prices'].get('MELON', 0)} | Milk Price: ${market['prices'].get('MILK', 0)}")
