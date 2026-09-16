with open('agents/public_v16_rc5.py') as f:
    text = f.read()

text = text.replace('def agent(obs):', 'def v16_agent(obs):')

# We will just replace STRAWBERRY with TOMATO dynamically in the wrapper!
text += '''
# --- V061 WRAPPER (TOMATO FRONTRUNNER) ---
def agent(obs):
    import json, base64, zlib
    if not hasattr(agent, "_patched"):
        agent._patched = True
        # Patch the global _ACTIONS list that v16_agent reads from!
        for act in _ACTIONS:
            if "farmer" in act:
                for i in range(len(act["farmer"])):
                    if act["farmer"][i] == "STRAWBERRY": act["farmer"][i] = "TOMATO"
            if "hands" in act:
                for hand in act["hands"]:
                    for i in range(len(hand)):
                        if hand[i] == "STRAWBERRY": hand[i] = "TOMATO"
            if "market" in act:
                for order in act["market"]:
                    for i in range(len(order)):
                        if order[i] == "STRAWBERRY": order[i] = "TOMATO"
                        
    # Run the V16 agent which now reads the patched _ACTIONS
    action = v16_agent(obs)
    
    # Also apply the V060 Melon Frontrunner logic!
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
'''

with open('agents/v061_tomato_frontrunner.py', 'w') as f:
    f.write(text)
print("Created V061 successfully!")
