import os
import sys
import pickle
import numpy as np

# Load trained models at module level
try:
    with open("RESEARCH/kaggle_loop/training/models/opponent_classifier.pkl", "rb") as f:
        opp_classifier = pickle.load(f)
    with open("RESEARCH/kaggle_loop/training/models/value_model.pkl", "rb") as f:
        value_model = pickle.load(f)
except Exception:
    opp_classifier = None
    value_model = None

_STATE = {
    "strategy": "STRAWBERRY", 
    "locked_in": False
}

def extract_live_features(obs, player):
    # Base economic features
    step = obs.get("step", 0)
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    
    farms = obs.get("farms", [])
    if len(farms) < 2:
        return None
        
    my_farm = farms[player]
    opp_farm = farms[1 - player]
    
    my_money = my_farm.get("money", 0)
    opp_money = opp_farm.get("money", 0)
    
    market = obs.get("market", {})
    market_inv = market.get("inventory", {})
    
    m_wheat = market_inv.get("WHEAT", 10000) - 10000
    m_melon = market_inv.get("MELON", 10000) - 10000
    m_strawberry = market_inv.get("STRAWBERRY", 10000) - 10000
    m_milk = market_inv.get("MILK", 10000) - 10000
    m_wool = market_inv.get("WOOL", 10000) - 10000
    m_carrot = market_inv.get("CARROT", 10000) - 10000
    
    my_melons, my_strawberries, my_cows, my_sheep = 0, 0, 0, 0
    for row in my_farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict):
                if tile.get("kind") == "PLANT":
                    crop = tile.get("crop")
                    if crop == "MELON": my_melons += 1
                    if crop == "STRAWBERRY": my_strawberries += 1
                elif tile.get("kind") in ["COOP", "PASTURE"]:
                    animal = tile.get("animal")
                    if animal == "COW": my_cows += 1
                    if animal == "SHEEP": my_sheep += 1
                    
    opp_melons, opp_strawberries, opp_cows, opp_sheep = 0, 0, 0, 0
    for row in opp_farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict):
                if tile.get("kind") == "PLANT":
                    crop = tile.get("crop")
                    if crop == "MELON": opp_melons += 1
                    if crop == "STRAWBERRY": opp_strawberries += 1
                elif tile.get("kind") in ["COOP", "PASTURE"]:
                    animal = tile.get("animal")
                    if animal == "COW": opp_cows += 1
                    if animal == "SHEEP": opp_sheep += 1
                    
    my_hands = len(my_farm.get("hands", []))
    opp_hands = len(opp_farm.get("hands", []))
    
    return np.array([
        day, hour, my_money, opp_money, m_wheat, m_melon, m_strawberry, 
        m_milk, m_wool, m_carrot, my_melons, my_strawberries, my_cows, my_sheep,
        opp_melons, opp_strawberries, opp_cows, opp_sheep, my_hands, opp_hands
    ], dtype=np.float32)

def agent(obs, configuration=None):
    try:
        sys.path.append("experiments/meta_classifier")
        import strat_melon
        import strat_strawberry
        
        step = obs.get("step", 0)
        player = obs.get("player", 0)
        
        # Every 24 steps (1 day), re-evaluate macro plan using Value Model
        if step % 24 == 0 and opp_classifier is not None and value_model is not None and not _STATE["locked_in"]:
            feats = extract_live_features(obs, player)
            if feats is not None:
                # 1. Classify opponent
                opp_arch = opp_classifier.predict(feats.reshape(1, -1))[0]
                
                # 2. Counterfactual Search: evaluate our two macro plans
                # Actually, in a real scenario, we'd simulate the step forward.
                # For this prototype, we'll map opponent archetype to hardcoded orthogonal plans
                # 0 = MELON_RUSH -> Play STRAWBERRY
                # 1 = LIVESTOCK_RUSH -> Play MELON
                # 2 = STRAWBERRY/BALANCED -> Play MELON (to avoid berry crash)
                
                if opp_arch == 0:
                    _STATE["strategy"] = "STRAWBERRY"
                elif opp_arch == 1:
                    _STATE["strategy"] = "MELON"
                else:
                    _STATE["strategy"] = "MELON"
                    
                # We can also query the value model just to see its prediction
                win_prob = value_model.predict_proba(feats.reshape(1, -1))[0][1]
                # In full implementation, we'd loop over plans, modify `feats` hypothetically, and select max win_prob.
                
        # Dispatch
        if _STATE["strategy"] == "MELON":
            return strat_melon.agent(obs, configuration)
        else:
            return strat_strawberry.agent(obs, configuration)
            
    except Exception as e:
        farms = obs.get("farms", [])
        farm = farms[obs.get("player", 0)] if len(farms) > obs.get("player", 0) else {}
        hands = farm.get("hands", [])
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in hands],
            "market": []
        }
