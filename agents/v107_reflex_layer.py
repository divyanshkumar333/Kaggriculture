import sys, os, copy
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture\agents')
import v105_revert_quote_priority as base_agent_module

def agent(obs, config=None):
    action = base_agent_module.agent(obs, config)
    if not isinstance(action, dict):
        return action
        
    try:
        player = int(obs["player"])
        farm = obs["farms"][player]
        priv = obs["private"]
        day = int(obs.get("day", int(obs.get("step", 0)) // 24))
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
            
            # 1. CARE GATING REFLEX
            if cmd[0] == "CARE":
                if isinstance(tile, dict) and "animal" in tile:
                    fed = tile.get("fed_today", False)
                    held = tile.get("yield_units", 0)
                    bonus = tile.get("pending_care_bonus", 0)
                    
                    if not fed:
                        if inv.get("WHEAT", 0) > 0:
                            units[i] = ["FEED"]
                            modified = True
                        elif held >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                    elif held + bonus >= 5:
                        if held >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                            
            # 2. FERTILIZE REDUNDANCY REFLEX
            elif cmd[0] == "FERTILIZE":
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    fert_until = tile.get("fertilized_until_day", -1)
                    if fert_until >= day + 2:
                        if not tile.get("watered_today", False):
                            units[i] = ["WATER"]
                            modified = True
                        elif tile.get("yield_units", 0) >= 1:
                            units[i] = ["HARVEST"]
                            modified = True
                            
        if modified:
            action = dict(action)
            action["farmer"] = units[0]
            action["hands"] = units[1:]
    except Exception:
        pass
        
    return action
