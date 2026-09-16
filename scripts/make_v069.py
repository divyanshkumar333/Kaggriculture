with open('agents/v066_ablation_strawberry_only.py') as f:
    text66 = f.read()

injection = '''
        # V069 Static Melon Dump
        melons = int(_get(shed, "MELON", 0) or 0)
        for inv in private.get("inventories", []):
            melons += int(_get(inv, "MELON", 0) or 0)
            
        if melons > 0:
            market = action.get("market", [])
            new_market = [order for order in market if not (len(order) >= 2 and order[0] == "SELL" and order[1] == "MELON")]
            new_market.insert(0, ["SELL", "MELON", melons])
            action["market"] = new_market[:10]
            
        state["last_action"] = _copy_action(action)
        return _align_hands(action, obs)
'''

target = '''        state["last_action"] = _copy_action(action)
        return _align_hands(action, obs)'''

text69 = text66.replace(target, injection)

with open('agents/v069_hybrid_spoiler.py', 'w') as f:
    f.write(text69)
    
print('Created v069 successfully.')
