import sys
import os

sys.path.append(os.path.dirname(__file__))

from v025_a_aggressive_cows import agent as cow_agent
from v059_strawberry_flywheel import agent as strawberry_agent

def count_opponent_cows(obs):
    opp = obs["farms"][1 - obs["player"]]
    cows = 0
    for row in opp["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and tile.get("animal") == "COW":
                cows += 1
    return cows

def count_opponent_melons(obs):
    opp = obs["farms"][1 - obs["player"]]
    melons = 0
    for row in opp["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                melons += 1
    return melons

def agent(obs):
    try:
        o_cows = count_opponent_cows(obs)
        if o_cows <= 1.5:
            return cow_agent(obs)
        elif o_cows <= 2.5:
            return strawberry_agent(obs)
        else:
            return cow_agent(obs)
    except Exception as e:
        print(f"ROUTER ERROR: {e}")
        return {}
