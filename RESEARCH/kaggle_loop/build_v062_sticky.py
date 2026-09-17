import os

def main():
    v057_code = open('agents/v057_generalized_spoiler.py').read()
    
    # We will rename the agent function in v057 to v057_agent
    v057_code = v057_code.replace("def agent(obs, configuration=None):", "def v057_agent(obs, configuration=None):")
    
    wrapper = """
# --- V062 DYNAMIC ROUTER ---
_ROUTER_STATE = {"opp_has_melons": False}

def agent(obs, configuration=None):
    # 1. Check if opponent has any Melons (planted)
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    opp_seat = 1 - seat
    farms = obs.get("farms", [])
    opp_farm = farms[opp_seat] if opp_seat < len(farms) else {}
    
    if not _ROUTER_STATE["opp_has_melons"]:
        # Check opponent tiles for Melon plants
        for row in opp_farm.get("tiles", []):
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON":
                    _ROUTER_STATE["opp_has_melons"] = True
                    break
            if _ROUTER_STATE["opp_has_melons"]:
                break
    
    # 2. Get the base action from v057
    action = v057_agent(obs, configuration)
    
    # 3. If opponent has Melons, we must aggressively DUMP our Melons
    if _ROUTER_STATE["opp_has_melons"]:
        farm = farms[seat] if seat < len(farms) else {}
        private = obs.get("private", {})
        
        melons = int(private.get("shed", {}).get("MELON", 0))
        for inv in private.get("inventories", []):
            melons += int(inv.get("MELON", 0))
            
        if melons > 0:
            new_market = []
            for order in action.get("market", []):
                if len(order) >= 2 and order[0] == "SELL" and order[1] == "MELON":
                    continue
                new_market.append(order)
            new_market.insert(0, ["SELL", "MELON", melons])
            action["market"] = new_market[:10]
            
    return action
"""

    with open('agents/v062_dynamic_melon_router.py', 'w') as f:
        f.write(v057_code + wrapper)

if __name__ == "__main__":
    main()
