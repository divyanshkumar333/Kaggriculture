import base64
import copy
import json
import math
import sys
import os
import importlib.util

def load_014():
    import sys
    import os
    path = os.path.abspath(os.path.join("agents", "014_robust_trace.py"))
    spec = importlib.util.spec_from_file_location("base_agent", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    base_agent = load_014()
except:
    pass

_PARASITE_STATE = {0: {}, 1: {}}

def get_projected_prices(obs):
    shops = obs["town"]["unlocked_shops"]
    day = obs["day"]
    remaining_days = max(0, 30 - day)
    
    daily = {
        "WHEAT": 1, "CARROT": 1, "TOMATO": 1, 
        "STRAWBERRY": 1, "MELON": 1, "EGG": 1, 
        "MILK": 1, "WOOL": 1, "FERTILIZER": 0
    }
    
    for shop in shops:
        if shop == "PET_CAFE": daily["CARROT"] += 6
        if shop == "FARMERS_MARKET": 
            daily["CARROT"] += 3
            daily["TOMATO"] += 3
            daily["STRAWBERRY"] += 3
            daily["WHEAT"] += 3
        if shop == "PIZZA_SHOP": 
            daily["TOMATO"] += 6
            daily["WHEAT"] += 6
            daily["MILK"] += 6
        if shop == "BAKERY": 
            daily["EGG"] += 6
            daily["MILK"] += 6
            daily["WHEAT"] += 12
        if shop == "BRUNCH_SPOT": 
            daily["EGG"] += 6
            daily["STRAWBERRY"] += 6
            daily["WHEAT"] += 6
        if shop == "ICE_CREAM_SHOP":
            daily["STRAWBERRY"] += 6
            daily["MILK"] += 6
            daily["WHEAT"] += 6
        if shop == "SMOOTHIE_SHOP":
            daily["STRAWBERRY"] += 6
            daily["MILK"] += 6
        if shop == "CLOTHING_STORE":
            daily["WOOL"] += 12
            
    market_inv = obs["market"]["inventory"]
    
    # Simple market price function clone for projection
    def sim_price(item, inv):
        from kaggle_environments.envs.kaggriculture.kaggriculture import market_price
        return market_price(item, inv)
        
    projections = {}
    for item in ["CARROT", "TOMATO", "STRAWBERRY", "MELON"]:
        proj_inv = market_inv[item] - (daily[item] * remaining_days)
        projections[item] = sim_price(item, proj_inv)
        
    return projections

def agent(obs, configuration=None):
    if "base_agent" not in globals():
        global base_agent
        base_agent = load_014()
        
    action = base_agent.agent(obs, configuration)
    
    player = obs["player"]
    step = obs["step"]
    day = obs["day"]
    me = obs["farms"][player]
    private = obs["private"]
    
    state = _PARASITE_STATE[player]
    if step == 0:
        state.clear()
        state["swarm_hands"] = []
        state["best_crop"] = "TOMATO"
        state["planted"] = []
        state["bought_se"] = False
        
    market = action.get("market", [])
    
    # 1. Project prices and lock in the best crop on day 15
    if step % 24 == 0 and day <= 15:
        projs = get_projected_prices(obs)
        best_crop = max(projs.keys(), key=lambda k: projs[k])
        state["best_crop"] = best_crop
        
    best_crop = state["best_crop"]
    
    # 2. Swarm Hiring (hire up to 6 extra hands, 1 per day to keep cost at 1 coin)
    trace = base_agent._ACTIONS[min(step, len(base_agent._ACTIONS)-1)]
    expected_hands = len(trace.get("hands", []))
    
    # Hire a hand if we haven't today and we want more swarm hands
    if me["hires_today"] == 0 and len(me["hands"]) - expected_hands < 6 and day >= 10 and me["money"] >= 2:
        market.insert(0, ["HIRE"])
        
    # 3. Buy SE quadrant
    # SE is unlocked by 3rd BUY_LAND.
    # If we have 5000+ money on day 15+, we spam BUY_LAND until we have SE.
    if day >= 15 and "SE" not in me["unlocked_quadrants"] and me["money"] >= 20000:
        market.insert(0, ["BUY_LAND"])
        
    # 4. Swarm Actions
    actual_hands = len(me["hands"])
    hands_actions = action.get("hands", [])
    while len(hands_actions) < actual_hands:
        hands_actions.append(["PASS"])
        
    swarm_start_idx = expected_hands
    
    if "SE" in me["unlocked_quadrants"]:
        # We own SE, let's plant!
        # SE tiles: x in 5..9, y in 5..9
        # Shed access is (5,5)
        se_tiles = []
        for x in range(5, 10):
            for y in range(5, 10):
                if (x, y) != (5,5):
                    se_tiles.append((x, y))
                    
        # Filter to empty tiles
        empty_se = []
        for tx, ty in se_tiles:
            t = me["tiles"][ty][tx]
            if t is None:
                empty_se.append((tx, ty))
                
        # Update planted state
        new_planted = []
        needs_water = []
        needs_harvest = []
        
        for tx, ty in state["planted"]:
            t = me["tiles"][ty][tx]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                new_planted.append((tx, ty))
                if not t.get("watered_today"):
                    needs_water.append((tx, ty))
                if t.get("yield_units", 0) > 0:
                    needs_harvest.append((tx, ty))
        state["planted"] = new_planted
        
        # Ensure we have seeds
        seeds = private["seeds"].get(best_crop, 0)
        target_plants = min(15, len(se_tiles))
        plants_needed = target_plants - len(state["planted"])
        
        if plants_needed > seeds and me["money"] >= 200:
            # Buy seeds (only 1 order per turn, so just append)
            if not any(order[0] == "BUY_SEED" and order[1] == best_crop for order in market):
                market.append(["BUY_SEED", best_crop, plants_needed - seeds])
                
        # Assign tasks to swarm hands
        idle_hands = list(range(swarm_start_idx, actual_hands))
        
        # Helper to assign movement or action
        def assign_task(h_idx, tx, ty, act):
            hx, hy = me["hands"][h_idx]
            if (hx, hy) != (tx, ty):
                if hx < tx: hands_actions[h_idx] = ["EAST"]
                elif hx > tx: hands_actions[h_idx] = ["WEST"]
                elif hy < ty: hands_actions[h_idx] = ["SOUTH"]
                elif hy > ty: hands_actions[h_idx] = ["NORTH"]
            else:
                hands_actions[h_idx] = act
                
        # Task priority: DROP > HARVEST > WATER > PLANT > IDLE
        for h_idx in idle_hands:
            hand_inv = private["inventories"][h_idx + 1] if (h_idx + 1) < len(private["inventories"]) else {}
            hx, hy = me["hands"][h_idx]
            
            if sum(hand_inv.values()) >= 5 or (sum(hand_inv.values()) > 0 and not needs_harvest and not needs_water and not empty_se):
                assign_task(h_idx, 5, 5, ["DROP"])
            elif needs_harvest:
                tx, ty = needs_harvest.pop(0)
                assign_task(h_idx, tx, ty, ["HARVEST"])
            elif needs_water:
                tx, ty = needs_water.pop(0)
                assign_task(h_idx, tx, ty, ["WATER"])
            elif empty_se and seeds > 0 and len(state["planted"]) < target_plants:
                tx, ty = empty_se.pop(0)
                assign_task(h_idx, tx, ty, ["PLANT", best_crop])
                state["planted"].append((tx, ty))
                seeds -= 1
            else:
                # Move out of the way or stand still
                hands_actions[h_idx] = ["PASS"]
                
    # At turn 718, SELL ALL HOARDED CROPS
    if step >= 717:
        hoarded = private["shed"].get(best_crop, 0)
        if hoarded > 0:
            market.insert(0, ["SELL", best_crop, hoarded])
            
    action["hands"] = hands_actions
    action["market"] = market[:10]
    
    return action
