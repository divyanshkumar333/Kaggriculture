from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

agent_a = load_agent("agents/v020_a_control.py")
agent_opp = load_agent("agents/v005_d_combined.py")

for s in [101, 102, 103, 104, 105]:
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env.run([agent_a, agent_opp])
    f0 = env.steps[-1][0].reward
    f1 = env.steps[-1][1].reward
    print(f"Seed {s}: P0 (Control) = ${f0:,.0f} | P1 (V005-D Animal) = ${f1:,.0f} | Winner: {'P0 (Control)' if f0 > f1 else 'P1 (Animal)'}")
