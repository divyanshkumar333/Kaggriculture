with open('agents/public_v16_rc5.py') as f:
    text = f.read()

text = text.replace('def agent(obs):', 'def v16_agent(obs):')

text += '''
# --- V063 WRAPPER (STRAWBERRY FRONTRUNNER) ---
# Dumps Melons AND Strawberries immediately to frontrun the mirror match crash!
def agent(obs):
    import json, base64, zlib
    if not hasattr(agent, "_patched"):
        agent._patched = True
        
    action = v16_agent(obs)
    
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farms = obs.get("farms", [])
    farm = farms[seat] if seat < len(farms) else {}
    private = obs.get("private", {})
    
    # 1. Count Melons and Strawberries in inventory
    melons = int(private.get("shed", {}).get("MELON", 0))
    strawberries = int(private.get("shed", {}).get("STRAWBERRY", 0))
    for inv in private.get("inventories", []):
        melons += int(inv.get("MELON", 0))
        strawberries += int(inv.get("STRAWBERRY", 0))
        
    new_market = []
    # Filter out existing MELON and STRAWBERRY sell orders from V16
    for order in action.get("market", []):
        if len(order) >= 2 and order[0] == "SELL" and order[1] in ("MELON", "STRAWBERRY"):
            continue
        new_market.append(order)
        
    # 2. Melon Frontrunner (DUMP ALL MELONS IMMEDIATELY)
    if melons > 0:
        new_market.insert(0, ["SELL", "MELON", melons])
        
    # 3. Strawberry Frontrunner (DUMP ALL STRAWBERRIES IMMEDIATELY)
    if strawberries > 0:
        # Insert AFTER melons so Melons always get top priority on Day 10 Hour 0
        insert_idx = 1 if melons > 0 else 0
        new_market.insert(insert_idx, ["SELL", "STRAWBERRY", strawberries])
        
    action["market"] = new_market[:10]
        
    return action
'''

with open('agents/v063_strawberry_frontrunner.py', 'w') as f:
    f.write(text)
print("Created V063 successfully!")
