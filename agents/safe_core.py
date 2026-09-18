def safe_get(obj, key, default=None):
    """
    Safely retrieves a value from a dictionary or Kaggle Observation object.
    Catches ALL exceptions (AttributeError, KeyError, TypeError, etc) and returns the default.
    Do not use dictionary methods like .get() directly on Kaggle objects.
    """
    try:
        # Some Kaggle Observation objects support __getitem__ but not .get()
        if hasattr(obj, '__getitem__'):
            try:
                val = obj[key]
                if val is not None:
                    return val
            except (KeyError, IndexError, TypeError):
                pass
        
        # Fallback to getattr if it's an object property
        if hasattr(obj, key):
            val = getattr(obj, key)
            if val is not None:
                return val
                
    except Exception:
        pass
        
    return default

def safe_parse_obs(obs):
    """
    Takes the raw Kaggle observation and returns a perfectly safe,
    standardized pure Python dictionary tree, eliminating all risk of runtime exceptions
    when nested structures are accessed.
    """
    player = safe_get(obs, "player", 0)
    step = safe_get(obs, "step", 0)
    day = safe_get(obs, "day", 0)
    hour = safe_get(obs, "hour", 0)
    
    farms_raw = safe_get(obs, "farms", [])
    farms = []
    
    # Safely parse farms
    try:
        # Cast to list if possible
        if not isinstance(farms_raw, list):
            farms_raw = list(farms_raw)
            
        for f in farms_raw:
            farm_dict = {
                "money": safe_get(f, "money", 0),
                "farmer": safe_get(f, "farmer", [0, 0]),
                "hands": safe_get(f, "hands", []),
                "unlocked_quadrants": safe_get(f, "unlocked_quadrants", ["NW"]),
                "hires_today": safe_get(f, "hires_today", 0)
            }
            
            # Safe tiles extraction
            tiles_raw = safe_get(f, "tiles", [])
            safe_tiles = []
            try:
                for row in tiles_raw:
                    safe_row = []
                    try:
                        for tile in row:
                            if tile is None or tile == "LOCKED":
                                safe_row.append(tile)
                            elif hasattr(tile, '__getitem__') or isinstance(tile, dict):
                                # It's a plant, weed, coop, or pasture
                                safe_tile_dict = {}
                                for k in ["kind", "crop", "animal", "planted_day", "yield_units", 
                                          "watered_today", "consecutive_unwatered", "max_lifespan_step", 
                                          "fertilized_until_day", "placed_day", "fed_today", "consecutive_unfed", 
                                          "cared_today", "fertilizer_available", "pending_care_bonus"]:
                                    val = safe_get(tile, k)
                                    if val is not None:
                                        safe_tile_dict[k] = val
                                safe_row.append(safe_tile_dict)
                            else:
                                safe_row.append(None)
                    except Exception:
                        pass
                    safe_tiles.append(safe_row)
            except Exception:
                pass
            
            farm_dict["tiles"] = safe_tiles
            farms.append(farm_dict)
    except Exception:
        pass

    # Ensure 2 farms always exist
    while len(farms) < 2:
        farms.append({"money": 0, "farmer": [0,0], "hands": [], "unlocked_quadrants": ["NW"], "hires_today": 0, "tiles": []})

    private_raw = safe_get(obs, "private", {})
    private = {
        "shed": safe_get(private_raw, "shed", {}),
        "seeds": safe_get(private_raw, "seeds", {}),
        "inventories": safe_get(private_raw, "inventories", [])
    }
    
    market_raw = safe_get(obs, "market", {})
    market = {
        "inventory": safe_get(market_raw, "inventory", {}),
        "prices": safe_get(market_raw, "prices", {})
    }
    
    town_raw = safe_get(obs, "town", {})
    town = {
        "unlocked_shops": safe_get(town_raw, "unlocked_shops", [])
    }

    return {
        "player": player,
        "step": step,
        "day": day,
        "hour": hour,
        "farms": farms,
        "private": private,
        "market": market,
        "town": town
    }
