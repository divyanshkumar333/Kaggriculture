with open('agents/public_v16_rc5.py') as f:
    text = f.read()

# Replace V16's agent with v16_agent
text = text.replace('def agent(obs):', 'def v16_agent(obs):')

# Append my wrapper
text += """
# --- V060 WRAPPER ---
def agent(obs):
    action = v16_agent(obs)
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

with open('agents/v060_melon_frontrunner.py', 'w') as f:
    f.write(text)
print("Created v060!")
