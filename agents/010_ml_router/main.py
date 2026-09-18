from cow_agent import agent as cow_agent
from strawberry_agent import agent as strawberry_agent

def count_opponent_cows(obs):
    opp = obs["farms"][1 - obs["player"]]
    cows = 0
    for row in opp["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal") == "COW":
                cows += 1
    return cows

def agent(obs):
    try:
        o_cows = count_opponent_cows(obs)
        
        # ML Router logic (Decision Tree from 360,000+ Kaggle Replay steps)
        if o_cows <= 1.5:
            return cow_agent(obs)
        elif o_cows <= 2.5:
            return strawberry_agent(obs)
        else:
            return cow_agent(obs)
    except Exception as e:
        # Fallback to PASS so we don't crash
        return {}
