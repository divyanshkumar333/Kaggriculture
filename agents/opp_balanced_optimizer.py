# Adversarial Opponent 2: Balanced Optimizer
# Balances Carrots (short cycle, crash-resistant) and Melons with early land expansion.
from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
import os

def agent(obs):
    try:
        player = obs["player"]
        my_farm = obs["farms"][player]
        private = obs["private"]
        money = my_farm["money"]
        shed = private.get("shed", {})
        seeds = private.get("seeds", {})
        day = obs["day"]
        hour = obs["hour"]
        fx, fy = my_farm["farmer"]
        tiles = my_farm["tiles"]
        
        market_actions = []
        
        # Sell produce
        for prod, qty in shed.items():
            if qty > 0:
                market_actions.append(["SELL", prod, min(qty, 10)])
                
        # Land Expansion
        unlocked = my_farm.get("unlocked_quadrants", [])
        if len(unlocked) == 1 and money > 1100:
            market_actions.append(["BUY_LAND"])
        elif len(unlocked) == 2 and money > 2200:
            market_actions.append(["BUY_LAND"])
            
        # Balanced seed purchase (Carrots + Melons)
        if day < 20:
            if seeds.get("MELON", 0) < 3 and money > 150:
                market_actions.append(["BUY_SEED", "MELON", 3])
            if seeds.get("CARROT", 0) < 4 and money > 100:
                market_actions.append(["BUY_SEED", "CARROT", 4])
        elif day < 26:
            # Late season: Carrots only
            if seeds.get("CARROT", 0) < 5 and money > 100:
                market_actions.append(["BUY_SEED", "CARROT", 5])
                
        # Labor hiring
        if len(my_farm.get("hands", [])) < 3 and money > 100:
            market_actions.append(["HIRE"])
            
        # Farmer action
        curr_tile = tiles[fy][fx]
        farmer_action = ["PASS"]
        if isinstance(curr_tile, dict) and curr_tile.get("kind") == "PLANT":
            crop = curr_tile.get("crop", "")
            first_yield = CROPS.get(crop, {}).get("first_yield_day", 999)
            if curr_tile.get("yield_units", 0) > 0 and (day - curr_tile.get("planted_day", 0)) >= first_yield:
                farmer_action = ["HARVEST"]
            elif not curr_tile.get("watered_today", True):
                farmer_action = ["WATER"]
            else:
                farmer_action = ["SOUTH"] if fy < 8 else ["WEST"]
        elif curr_tile is None:
            if seeds.get("MELON", 0) > 0 and day < 20:
                farmer_action = ["PLANT", "MELON"]
            elif seeds.get("CARROT", 0) > 0 and day < 27:
                farmer_action = ["PLANT", "CARROT"]
            else:
                farmer_action = ["EAST"]
        else:
            farmer_action = ["NORTH"] if fy > 0 else ["EAST"]
            
        # Hands actions
        hands_actions = []
        for hx, hy in my_farm.get("hands", []):
            htile = tiles[hy][hx]
            if isinstance(htile, dict) and htile.get("kind") == "PLANT":
                crop = htile.get("crop", "")
                first_yield = CROPS.get(crop, {}).get("first_yield_day", 999)
                if not htile.get("watered_today", True):
                    hands_actions.append(["WATER"])
                elif htile.get("yield_units", 0) > 0 and (day - htile.get("planted_day", 0)) >= first_yield:
                    hands_actions.append(["HARVEST"])
                else:
                    hands_actions.append(["WEST"] if hx > 0 else ["SOUTH"])
            elif htile is None:
                if seeds.get("CARROT", 0) > 0 and day < 27:
                    hands_actions.append(["PLANT", "CARROT"])
                elif seeds.get("MELON", 0) > 0 and day < 20:
                    hands_actions.append(["PLANT", "MELON"])
                else:
                    hands_actions.append(["EAST"] if hx < 8 else ["NORTH"])
            else:
                hands_actions.append(["NORTH"] if hy > 0 else ["EAST"])
                
        return {
            "farmer": farmer_action,
            "hands": hands_actions,
            "market": market_actions[:10]
        }
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
