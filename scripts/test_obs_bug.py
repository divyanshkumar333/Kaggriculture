from kaggle_environments import make

def agent_0(obs, conf):
    print(f"P0 Step from kaggle_environments: {obs['step']}")
    return {"farmer": ["PASS"], "hands": [], "market": []}

def agent_1(obs, conf):
    print(f"P1 Step from kaggle_environments: {obs['step']}")
    return {"farmer": ["PASS"], "hands": [], "market": []}

if __name__ == "__main__":
    env = make("kaggriculture", configuration={"episodeSteps": 5}, debug=True)
    env.run([agent_0, agent_1])
