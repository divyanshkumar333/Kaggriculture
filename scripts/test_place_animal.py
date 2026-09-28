from kaggle_environments import make

def test_agent(obs):
    day = obs["day"]
    hour = obs["hour"]
    me = obs["farms"][obs["player"]]
    inv = obs["private"]["inventories"][0]
    shed = obs["private"]["shed"]
    print(f"D{day} H{hour} | Shed: {shed} | Inv: {inv} | Farmer: {me['farmer']}")
    
    if day == 0 and hour == 0:
        # Buy Sheep, Build Pasture
        return {"farmer": ["BUILD_PASTURE"], "hands": [], "market": [["BUY_ANIMAL", "SHEEP", 1]]}
    elif day == 0 and hour == 1:
        # Place Sheep! (farmer is still on the pasture)
        return {"farmer": ["PLACE", "SHEEP", 1], "hands": [], "market": []}
    return {"farmer": ["PASS"], "hands": [], "market": []}

env = make("kaggriculture", configuration={"episodeSteps": 5})
env.run([test_agent, "random"])
for i, step in enumerate(env.steps):
    print(f"Step {i}:")
    print(f"  P1 Inv: {step[0].observation['private']['inventories'][0]}")
    print(f"  P1 Shed: {step[0].observation['private']['shed']}")
    tiles = step[0].observation["farms"][0]["tiles"]
    # Check what is at (4,4) (which is where the farmer starts)
    print(f"  Tile (4,4): {tiles[4][4]}")
