import base64
import copy
import json
import math
import zlib
import sys
import os

# We will load the logic of 014 dynamically to avoid code duplication,
# or we can just import it directly since it's in the same directory.
import importlib.util

def load_014():
    import sys
    import os
    path = os.path.abspath(os.path.join("agents", "014_robust_trace.py"))
    spec = importlib.util.spec_from_file_location("base_agent", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_agent = load_014()

# State for the parasite
_PARASITE_STATE = {0: {}, 1: {}}

def agent(obs, configuration=None):
    # Get base action
    action = base_agent.agent(obs, configuration)
    
    player = obs["player"]
    step = obs["step"]
    day = obs["day"]
    me = obs["farms"][player]
    private = obs["private"]
    
    state = _PARASITE_STATE[player]
    if step == 0:
        state.clear()
        
    market = action.get("market", [])
    
    # We want to intercept the market actions to buy TOMATO seeds on day 0
    if step == 0:
        # We need 20 TOMATO seeds (1000 coins).
        # But wait, does 014 spend all its money on day 0?
        # V16 buys 2 WHEAT seeds and 1 COW.
        # We will buy 4 TOMATO seeds (200 coins).
        market.insert(0, ["BUY_SEED", "TOMATO", 4])
        
    # We need to hire a hand.
    # 014 hires hands on specific days.
    # We will just inject a HIRE order on day 1 (step 24) to ensure we have an extra hand.
    if step == 24:
        market.insert(0, ["HIRE"])
        
    # How many hands does the base trace expect?
    # We can check base_agent._ACTIONS[step]["hands"]
    trace = base_agent._ACTIONS[min(step, len(base_agent._ACTIONS)-1)]
    expected_hands = len(trace.get("hands", []))
    actual_hands = len(me["hands"])
    
    my_hand_idx = expected_hands # The extra hand we hired
    
    hands_actions = action.get("hands", [])
    while len(hands_actions) < actual_hands:
        hands_actions.append(["PASS"])
        
    # If our extra hand exists, control it
    if my_hand_idx < actual_hands:
        hx, hy = me["hands"][my_hand_idx]
        
        # Parasite logic for the extra hand
        # 1. Plant 4 tomatoes at specific locations.
        targets = [(3,1), (3,2), (4,1), (5,1)] # Safe locations away from V16? V16 uses NW.
        # Wait, V16 uses NW. Let's plant in NE?
        # V16 unlocks NE on day 5. We can't plant in NE until then.
        # Let's plant at (4,6), (4,7), (5,6), (5,7) - South of shed?
        # V16 unlocks SW and SE late.
        # Let's just find ANY empty unlocked tile that V16 isn't using.
        
        # Find 4 empty tiles in NW
        empty_tiles = []
        for ty in range(5):
            for tx in range(5):
                t = me["tiles"][ty][tx]
                if t is None:
                    empty_tiles.append((tx, ty))
                    
        # State memory for our planted tiles
        if "planted" not in state:
            state["planted"] = []
            
        my_plants = state["planted"]
        
        # Plant if we have seeds
        seeds = private["seeds"].get("TOMATO", 0)
        
        if seeds > 0 and len(my_plants) < 4:
            # Plant on the first empty tile
            if empty_tiles:
                tx, ty = empty_tiles[0]
                if (hx, hy) != (tx, ty):
                    if hx < tx: hands_actions[my_hand_idx] = ["EAST"]
                    elif hx > tx: hands_actions[my_hand_idx] = ["WEST"]
                    elif hy < ty: hands_actions[my_hand_idx] = ["SOUTH"]
                    elif hy > ty: hands_actions[my_hand_idx] = ["NORTH"]
                else:
                    hands_actions[my_hand_idx] = ["PLANT", "TOMATO"]
                    my_plants.append((tx, ty))
                    
        else:
            # Water and harvest our plants
            needs_water = []
            needs_harvest = []
            for tx, ty in my_plants:
                t = me["tiles"][ty][tx]
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    if not t.get("watered_today"):
                        needs_water.append((tx, ty))
                    if t.get("yield_units", 0) > 0:
                        needs_harvest.append((tx, ty))
                        
            # Hand inventory
            hand_inv = private["inventories"][my_hand_idx + 1] if (my_hand_idx + 1) < len(private["inventories"]) else {}
            
            if sum(hand_inv.values()) >= 5: # carry up to 5 before dropping to save time
                if (hx, hy) not in [(4,4), (5,4), (4,5), (5,5)]:
                    if hx < 4: hands_actions[my_hand_idx] = ["EAST"]
                    elif hx > 5: hands_actions[my_hand_idx] = ["WEST"]
                    elif hy < 4: hands_actions[my_hand_idx] = ["SOUTH"]
                    elif hy > 5: hands_actions[my_hand_idx] = ["NORTH"]
                else:
                    hands_actions[my_hand_idx] = ["DROP"]
            elif needs_harvest:
                tx, ty = needs_harvest[0]
                if (hx, hy) != (tx, ty):
                    if hx < tx: hands_actions[my_hand_idx] = ["EAST"]
                    elif hx > tx: hands_actions[my_hand_idx] = ["WEST"]
                    elif hy < ty: hands_actions[my_hand_idx] = ["SOUTH"]
                    elif hy > ty: hands_actions[my_hand_idx] = ["NORTH"]
                else:
                    hands_actions[my_hand_idx] = ["HARVEST"]
            elif needs_water:
                tx, ty = needs_water[0]
                if (hx, hy) != (tx, ty):
                    if hx < tx: hands_actions[my_hand_idx] = ["EAST"]
                    elif hx > tx: hands_actions[my_hand_idx] = ["WEST"]
                    elif hy < ty: hands_actions[my_hand_idx] = ["SOUTH"]
                    elif hy > ty: hands_actions[my_hand_idx] = ["NORTH"]
                else:
                    hands_actions[my_hand_idx] = ["WATER"]
            elif sum(hand_inv.values()) > 0: # Drop at end of day or idle
                if (hx, hy) not in [(4,4), (5,4), (4,5), (5,5)]:
                    if hx < 4: hands_actions[my_hand_idx] = ["EAST"]
                    elif hx > 5: hands_actions[my_hand_idx] = ["WEST"]
                    elif hy < 4: hands_actions[my_hand_idx] = ["SOUTH"]
                    elif hy > 5: hands_actions[my_hand_idx] = ["NORTH"]
                else:
                    hands_actions[my_hand_idx] = ["DROP"]
                    
    # At turn 718, SELL ALL TOMATOES
    if step == 718:
        tomatoes = private["shed"].get("TOMATO", 0)
        if tomatoes > 0:
            market.append(["SELL", "TOMATO", tomatoes])
            
    action["hands"] = hands_actions
    action["market"] = market[:10]
    
    return action
