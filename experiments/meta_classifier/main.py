import sys
import copy
import strat_melon
import strat_strawberry

_STATE = {
    "classification_done": False,
    "strategy": "STRAWBERRY", # Default safe strategy
    "opp_melons_seen": 0,
    "opp_livestock_seen": 0,
}

def agent(obs, configuration=None):
    try:
        step = obs.get("step", 0)
        player = obs.get("player", 0)
        opp_idx = 1 - player
        
        # Safe extraction of opponent farms
        farms = obs.get("farms", [])
        if len(farms) > opp_idx:
            opp_farm = farms[opp_idx]
            
            # Observe opponent tiles until step 72 (Day 3 start)
            if step <= 72 and not _STATE["classification_done"]:
                opp_tiles = opp_farm.get("tiles", [])
                melon_count = 0
                livestock_count = 0
                
                for row in opp_tiles:
                    if not row: continue
                    for tile in row:
                        if isinstance(tile, dict):
                            if tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                                melon_count += 1
                            elif tile.get("kind") in ("COOP", "PASTURE") and tile.get("animal") in ("COW", "SHEEP", "GOOSE"):
                                livestock_count += 1
                                
                _STATE["opp_melons_seen"] = max(_STATE["opp_melons_seen"], melon_count)
                _STATE["opp_livestock_seen"] = max(_STATE["opp_livestock_seen"], livestock_count)
                
            if step == 73 and not _STATE["classification_done"]:
                _STATE["classification_done"] = True
                
                # Decision Matrix
                if _STATE["opp_melons_seen"] >= 8:
                    # Opponent is rushing Melons. Play Strawberry flywheel to dodge the melon crash.
                    _STATE["strategy"] = "STRAWBERRY"
                elif _STATE["opp_livestock_seen"] >= 2:
                    # Opponent is rushing livestock (Cows/Sheep). Play Melon heavy since milk will crash.
                    _STATE["strategy"] = "MELON"
                else:
                    # Default balanced/aggressive
                    _STATE["strategy"] = "STRAWBERRY"
                    
        # Dispatch
        if _STATE["strategy"] == "MELON":
            return strat_melon.agent(obs, configuration)
        else:
            return strat_strawberry.agent(obs, configuration)
            
    except Exception as e:
        # Fallback to avoid crashing
        farms = obs.get("farms", [])
        farm = farms[obs.get("player", 0)] if len(farms) > obs.get("player", 0) else {}
        hands = farm.get("hands", [])
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in hands],
            "market": []
        }
