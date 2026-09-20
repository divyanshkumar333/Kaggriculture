def extract_opponent_features(obs):
    """
    Given the environment observation, extract legally observable features about the opponent.
    Returns a dictionary of features.
    """
    player = obs["player"]
    opp_idx = 1 - player
    
    if "farms" not in obs:
        return {}
        
    opp_farm = obs["farms"][opp_idx]
    
    # 1. Labor
    num_hands = len(opp_farm.get("hands", []))
    total_workers = 1 + num_hands
    
    # 2. Livestock & Structures
    cows = 0
    sheep = 0
    geese = 0
    empty_pastures = 0
    
    # 3. Crops
    strawberries = 0
    melons = 0
    wheat = 0
    
    tiles = opp_farm.get("tiles", [])
    if not tiles:
        return {}
        
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                kind = t.get("kind")
                if kind == "PASTURE":
                    animal = t.get("animal")
                    if animal == "COW":
                        cows += 1
                    elif animal == "SHEEP":
                        sheep += 1
                    else:
                        empty_pastures += 1
                elif kind == "COOP":
                    animal = t.get("animal")
                    if animal == "GOOSE":
                        geese += 1
                elif kind == "PLANT":
                    crop = t.get("crop")
                    if crop == "STRAWBERRY":
                        strawberries += 1
                    elif crop == "MELON":
                        melons += 1
                    elif crop == "WHEAT":
                        wheat += 1
                        
    return {
        "opp_total_workers": total_workers,
        "opp_cows": cows,
        "opp_sheep": sheep,
        "opp_geese": geese,
        "opp_empty_pastures": empty_pastures,
        "opp_strawberries": strawberries,
        "opp_melons": melons,
        "opp_wheat": wheat,
        "opp_quadrants": len(opp_farm.get("unlocked_quadrants", ["NW"])),
        "opp_cash": opp_farm.get("money", 0)
    }
