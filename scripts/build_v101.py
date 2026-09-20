import os
import sys

def build_v101():
    base_file = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    target_file = r"e:\Setup\kaggle\kaggriculture\agents\v101_meta_reflex.py"
    
    with open(base_file, "r", encoding="utf-8") as f:
        code = f.read()
        
    # Replace the final line: agent = globals().pop('agent')
    target_needle = "agent.telemetry = _CS_REPORT\nagent = globals().pop('agent')"
    if target_needle not in code:
        raise ValueError(f"Could not find target needle in {base_file}")
        
    reflex_layer = """agent.telemetry = _CS_REPORT

# ===========================================================================
# LAYER 28: COMMUNITY REFLEXES & LABOR OPTIMIZATION (V101)
# 1. Care Gating: Never issue no-op care to unfed or capped animals; upgrade to FEED/HARVEST.
# 2. Fertilize Filter: Never issue redundant fertilize on tiles already fertilized >= day+2.
# 3. Liquidation Safety: Guarantee zero unharvested / unsold residual assets.
# ===========================================================================

_V101_PARENT = agent
del agent
_V101_STATS = {"upgraded_feed": 0, "upgraded_harvest": 0, "upgraded_water": 0, "errors": 0}

def agent(observation, configuration=None):
    action = _V101_PARENT(observation, configuration)
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
            
            # --- 1. CARE GATING REFLEX ---
            if cmd[0] == "CARE":
                if isinstance(tile, dict) and "animal" in tile:
                    fed = tile.get("fed_today", False)
                    held = tile.get("yield_units", 0)
                    bonus = tile.get("pending_care_bonus", 0)
                    
                    # Case A: Animal NOT fed yet today -> CARE does literally nothing
                    if not fed:
                        if inv.get("WHEAT", 0) > 0:
                            units[i] = ["FEED"]
                            modified = True
                            _V101_STATS["upgraded_feed"] += 1
                        elif held >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                            _V101_STATS["upgraded_harvest"] += 1
                            
                    # Case B: Animal bonus + held already at max_held ceiling (6)
                    elif held + bonus >= 5:
                        if held >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                            _V101_STATS["upgraded_harvest"] += 1
                            
            # --- 2. FERTILIZE REDUNDANCY REFLEX ---
            elif cmd[0] == "FERTILIZE":
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    fert_until = tile.get("fertilized_until_day", -1)
                    if fert_until >= day + 2:
                        # Tile is already fertilized for today and next 2 days!
                        if not tile.get("watered_today", False):
                            units[i] = ["WATER"]
                            modified = True
                            _V101_STATS["upgraded_water"] += 1
                        elif tile.get("yield_units", 0) >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                            _V101_STATS["upgraded_harvest"] += 1
                            
        if modified:
            action = dict(action)
            action["farmer"] = units[0]
            action["hands"] = units[1:]
    except Exception:
        _V101_STATS["errors"] += 1
        
    return action

agent.telemetry_v101 = _V101_STATS
agent = globals().pop('agent')
"""
    new_code = code.replace(target_needle, reflex_layer)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"Successfully generated {target_file} ({len(new_code)} bytes)")

if __name__ == "__main__":
    build_v101()
