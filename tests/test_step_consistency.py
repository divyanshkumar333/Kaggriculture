import sys
from kaggle_environments import make

def agent0(obs):
    print(f"Agent0 - step: {obs.get('step')}, day: {obs.get('day')}, hour: {obs.get('hour')}")
    return {"farmer": ["PASS"], "hands": [], "market": []}

def agent1(obs):
    print(f"Agent1 - step: {obs.get('step')}, day: {obs.get('day')}, hour: {obs.get('hour')}")
    return {"farmer": ["PASS"], "hands": [], "market": []}

if __name__ == "__main__":
    env = make("kaggriculture", configuration={"episodeSteps": 10}, debug=True)
    env.run([agent0, agent1])
    print("Test Complete.")
