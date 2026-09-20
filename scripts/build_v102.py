import os
import sys

def build_v102():
    base_file = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    target_file = r"e:\Setup\kaggle\kaggriculture\agents\v102_clean_reflex.py"
    
    with open(base_file, "r", encoding="utf-8") as f:
        code = f.read()
        
    target_needle = "agent.telemetry = _CS_REPORT\nagent = globals().pop('agent')"
    if target_needle not in code:
        raise ValueError(f"Could not find target needle in {base_file}")
        
    reflex_layer = """agent.telemetry = _CS_REPORT

# ===========================================================================
# LAYER 28: CLEAN REFLEX LAYER (V102)
# Zero Inventory Contamination:
# 1. Care Gate: If animal is NOT fed today and bonus is no-op, never issue CARE.
#    If the unit is carrying WHEAT on an unfed animal, FEED it!
# 2. Fertilize Gate: If tile is already fertilized (>= day+2), do not re-fertilize.
#    Instead, if standing on a plant that is unwatered today, WATER it!
# 3. Preserves worker inventory schedule exactly to prevent tape desynchronization.
# ===========================================================================

_V102_PARENT = agent
del agent
_V102_STATS = {"upgraded_feed": 0, "upgraded_water": 0, "saved_fert": 0, "errors": 0}

def agent(observation, configuration=None):
    action = _V102_PARENT(observation, configuration)
    if not isinstance(action, dict):
        return action
        
    try:
        player = int(observation["player"])
        farm = observation["farms"][player]
        priv = observation["private"]
        day = int(observation.get("day", int(observation.get("step", 0)) // 24))
        tiles = farm["tiles"]
        
        farmer_act = action.get("farmer") or ["PASS"]
        hands_acts = list(action.get("hands") or [])
        units = [farmer_act] + hands_acts
        
        positions = [farm["farmer"]] + list(farm["hands"] or [])
        inventories = list(priv.get("inventories") or [])
        
        modified = False
        for i in range(min(len(units), len(positions))):
            cmd = units[i]
            if not (isinstance(cmd, list) and cmd):
                continue
            pos = positions[i]
            x, y = int(pos[0]), int(pos[1])
            if not (0 <= x < 10 and 0 <= y < 10):
                continue
            tile = tiles[y][x]
            inv = inventories[i] if i < len(inventories) else {}
            
            # --- 1. CLEAN CARE GATING ---
            if cmd[0] == "CARE":
                if isinstance(tile, dict) and "animal" in tile:
                    fed = tile.get("fed_today", False)
                    # If animal is NOT fed today, CARE is 100% wasted turn
                    if not fed:
                        # If carrying wheat, feed it immediately (zero new inventory carried!)
                        if inv.get("WHEAT", 0) > 0:
                            units[i] = ["FEED"]
                            modified = True
                            _V102_STATS["upgraded_feed"] += 1
                        else:
                            # Do not issue useless CARE; PASS avoids engine no-op churn
                            units[i] = ["PASS"]
                            modified = True
                            
            # --- 2. CLEAN FERTILIZE FILTER ---
            elif cmd[0] == "FERTILIZE":
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    fert_until = tile.get("fertilized_until_day", -1)
                    if fert_until >= day + 2:
                        _V102_STATS["saved_fert"] += 1
                        # Tile already has active fertilizer!
                        # If not watered today, WATER it (requires 0 inventory, adds yield!)
                        if not tile.get("watered_today", False):
                            units[i] = ["WATER"]
                            modified = True
                            _V102_STATS["upgraded_water"] += 1
                        else:
                            # Avoid wasting fertilizer inventory!
                            units[i] = ["PASS"]
                            modified = True
                            
        if modified:
            action = dict(action)
            action["farmer"] = units[0]
            action["hands"] = units[1:]
    except Exception:
        _V102_STATS["errors"] += 1
        
    return action

agent.telemetry_v102 = _V102_STATS
agent = globals().pop('agent')
"""
    new_code = code.replace(target_needle, reflex_layer)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"Successfully generated {target_file} ({len(new_code)} bytes)")

if __name__ == "__main__":
    build_v102()
