from kaggle_environments import make
import sys
sys.path.append('e:/Setup/kaggle/kaggriculture/agents')
import generated_premium_route_1 as tape_agent

env = make("kaggriculture", configuration={"episodeSteps": 720})
env.run([tape_agent.agent, "random"])
final_state = env.steps[-1]
cash0 = final_state[0].reward
cash1 = final_state[1].reward

print(f"P1 (Tape) Cash: {cash0}")
print(f"P2 (Random) Cash: {cash1}")
