import sys
import copy
import strat_melon
import strat_strawberry

_STATE = {
    "classification_done": False,
    "strategy": "MELON", # Default safe strategy
    "opp_melons_seen": 0,
    "opp_livestock_seen": 0,
}

def agent(obs, configuration=None):
    try:
        # Fix for Kaggle Observation Struct vs local dict
        if hasattr(obs, 'step'):
            step = obs.step
            player = obs.player
            farms = getattr(obs, "farms", [])
        else:
            step = obs.get("step", 0)
            player = obs.get("player", 0)
            farms = obs.get("farms", [])
            
        opp_idx = 1 - player
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
                    # Default to strongest base strategy (Melon)
                    _STATE["strategy"] = "MELON"
                    
        # Dispatch
        if _STATE["strategy"] == "MELON":
            return strat_melon.agent(obs)
        else:
            return strat_strawberry.agent(obs)
            
    except Exception as e:
        import traceback
        import sys
        print(f"Agent Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        # Fallback to avoid crashing
        farms = getattr(obs, "farms", []) if hasattr(obs, "farms") else obs.get("farms", [])
        player = getattr(obs, "player", 0) if hasattr(obs, "player") else obs.get("player", 0)
        farm = farms[player] if len(farms) > player else {}
        hands = getattr(farm, "hands", []) if hasattr(farm, "hands") else farm.get("hands", [])
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in hands],
            "market": []
        }
