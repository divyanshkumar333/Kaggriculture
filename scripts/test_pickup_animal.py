from kaggle_environments import make

def test_agent(obs):
    day = obs["day"]
    hour = obs["hour"]
    me = obs["farms"][obs["player"]]
    inv = obs["private"]["inventories"][0]
    shed = obs["private"]["shed"]
    print(f"D{day} H{hour} | Shed: {shed} | Inv: {inv}")
    
    if day == 0 and hour == 0:
        return {"farmer": ["PASS"], "hands": [], "market": [["BUY_ANIMAL", "SHEEP", 1]]}
    elif day == 0 and hour == 1:
        return {"farmer": ["PASS"], "hands": [], "market": []}
    elif day == 0 and hour == 2:
        return {"farmer": ["PICKUP", "SHEEP", 1], "hands": [], "market": []}
    elif day == 0 and hour == 3:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    return {"farmer": ["PASS"], "hands": [], "market": []}

env = make("kaggriculture", configuration={"episodeSteps": 20})
env.run([test_agent, "random"])
for i, step in enumerate(env.steps):
    print(f"Step {i}:")
    print(f"  P1 Inv: {step[0].observation['private']['inventories'][0]}")
    print(f"  P1 Shed: {step[0].observation['private']['shed']}")

