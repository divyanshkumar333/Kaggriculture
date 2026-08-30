# Adversarial Opponent 1: Melon Flooder
# Aggressively plants Melons and expands land early to saturate the market.
from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
import os
import math

def agent(obs):
    try:
        player = obs["player"]
        my_farm = obs["farms"][player]
        private = obs["private"]
        market = obs.get("market", {})
        fx, fy = my_farm["farmer"]
        money = my_farm["money"]
        shed = private.get("shed", {})
        seeds = private.get("seeds", {})
        day = obs["day"]
        hour = obs["hour"]
        
        market_actions = []
        
        # Sell produce immediately
        for prod, qty in shed.items():
            if qty > 0:
                market_actions.append(["SELL", prod, min(qty, 10)])
                
        # Buy Melon seeds aggressively
        if seeds.get("MELON", 0) < 6 and money > 80 and day < 20:
            buy_count = min(money // 80, 5)
            if buy_count > 0:
                market_actions.append(["BUY_SEED", "MELON", buy_count])
                
        # Hire 1-2 workers if we have money
        if len(my_farm.get("hands", [])) < 3 and money > 200:
            market_actions.append(["HIRE"])
            
        # Buy land if money > 1500
        unlocked = my_farm.get("unlocked_quadrants", [])
        if len(unlocked) == 1 and money > 1200:
            market_actions.append(["BUY_LAND"])
            
        # Farmer action: Harvest if ready, Water if unwatered, Plant if empty
        tiles = my_farm["tiles"]
        curr_tile = tiles[fy][fx]
        farmer_action = ["PASS"]
        
        if isinstance(curr_tile, dict) and curr_tile.get("kind") == "PLANT":
            if curr_tile.get("yield_units", 0) > 0 and (day - curr_tile.get("planted_day", 0)) >= 10:
                farmer_action = ["HARVEST"]
            elif not curr_tile.get("watered_today", True):
                farmer_action = ["WATER"]
            else:
                farmer_action = ["WEST"] if fx > 0 else ["SOUTH"]
        elif curr_tile is None and seeds.get("MELON", 0) > 0 and day < 20:
            farmer_action = ["PLANT", "MELON"]
        else:
            # Move around to find unwatered or empty tiles
            farmer_action = ["EAST"] if (fx + fy) % 2 == 0 else ["NORTH"]
            
        # Worker actions
        hands_actions = []
        for hx, hy in my_farm.get("hands", []):
            htile = tiles[hy][hx]
            if isinstance(htile, dict) and htile.get("kind") == "PLANT":
                if not htile.get("watered_today", True):
                    hands_actions.append(["WATER"])
                elif htile.get("yield_units", 0) > 0 and (day - htile.get("planted_day", 0)) >= 10:
                    hands_actions.append(["HARVEST"])
                else:
                    hands_actions.append(["SOUTH"] if hy < 4 else ["WEST"])
            elif htile is None and seeds.get("MELON", 0) > 0 and day < 20:
                hands_actions.append(["PLANT", "MELON"])
            else:
                hands_actions.append(["NORTH"] if hy > 0 else ["EAST"])
                
        return {
            "farmer": farmer_action,
            "hands": hands_actions,
            "market": market_actions[:10]
        }
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
