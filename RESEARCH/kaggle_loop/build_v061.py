import os

def main():
    code = open('agents/v057_generalized_spoiler.py').read()
    
    wrapper = """
# --- V061 WRAPPER ---
def agent(obs, configuration=None):
    action = v057_agent(obs, configuration)
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = obs.get("farms", [])
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
    code = code.replace("def agent(obs, configuration=None):", "def v057_agent(obs, configuration=None):")
    code += wrapper
    
    with open('agents/v061_ultimate_melon_spoiler.py', 'w') as f:
        f.write(code)

if __name__ == "__main__":
    main()
