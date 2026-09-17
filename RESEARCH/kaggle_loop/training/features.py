import numpy as np

def extract_features(obs, player):
    """
    Extracts features from the raw Kaggriculture observation.
    Must ONLY use data available to 'player' (e.g. no opponent private info).
    """
    step = obs.get("step", 0)
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    
    farms = obs.get("farms", [])
    if len(farms) < 2:
        return None
        
    my_farm = farms[player]
    opp_farm = farms[1 - player]
    
    # Base economic features
    my_money = my_farm.get("money", 0)
    opp_money = opp_farm.get("money", 0) # Opponent money is public
    
    # Inventory
    market = obs.get("market", {})
    market_inv = market.get("inventory", {})
    
    m_wheat = market_inv.get("WHEAT", 10000) - 10000
    m_melon = market_inv.get("MELON", 10000) - 10000
    m_strawberry = market_inv.get("STRAWBERRY", 10000) - 10000
    m_milk = market_inv.get("MILK", 10000) - 10000
    m_wool = market_inv.get("WOOL", 10000) - 10000
    m_carrot = market_inv.get("CARROT", 10000) - 10000
    
    # My farm state
    my_melons = 0
    my_strawberries = 0
    my_cows = 0
    my_sheep = 0
    
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
                    
    # Opponent inferred state
    opp_melons = 0
    opp_strawberries = 0
    opp_cows = 0
    opp_sheep = 0
    
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
                    
    # Hands/workers count
    my_hands = len(my_farm.get("hands", []))
    opp_hands = len(opp_farm.get("hands", []))
    
    return np.array([
        day,
        hour,
        my_money,
        opp_money,
        m_wheat,
        m_melon,
        m_strawberry,
        m_milk,
        m_wool,
        m_carrot,
        my_melons,
        my_strawberries,
        my_cows,
        my_sheep,
        opp_melons,
        opp_strawberries,
        opp_cows,
        opp_sheep,
        my_hands,
        opp_hands
    ], dtype=np.float32)
