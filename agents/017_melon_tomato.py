def agent(obs, configuration=None):
    step = obs["step"]
    day = obs["day"]
    me = obs["farms"][obs["player"]]
    private = obs["private"]
    fx, fy = me["farmer"]
    
    market = []
    
    # 12-MELON config
    melon_targets = [
        (0,0), (1,0), (2,0),
        (0,1), (1,1), (2,1),
        (0,2), (1,2), (2,2),
        (0,3), (1,3), (2,3)
    ]
    # Hand assignments for melons
    hand_melon_targets = [
        [(0,0), (1,0), (2,0)], # Hand 0
        [(0,1), (1,1), (2,1)], # Hand 1
        [(0,2), (1,2), (2,2)], # Hand 2
        [(0,3), (1,3), (2,3)], # Hand 3
    ]
    
    # TOMATO targets for Main Farmer
    tomato_targets = [(0,4), (1,4), (2,4), (3,4)]
    
    # Day 0: Buy seeds and hire hands
    if step == 0:
        market.append(["BUY_SEED", "MELON", 12])
        market.append(["BUY_SEED", "TOMATO", 4])
        for _ in range(4):
            market.append(["HIRE"])
            
    # Market: Sell MELON from shed
    # We always sell MELON. We HOARD TOMATO until step 718.
    if step < 718:
        melons = private["shed"].get("MELON", 0)
        if melons > 0:
            market.append(["SELL", "MELON", melons])
    else:
        # Turn 718+: SELL EVERYTHING
        for item, qty in private["shed"].items():
            if qty > 0:
                market.append(["SELL", item, qty])
                
    farmer = ["PASS"]
    
    # Main Farmer Logic (Tomato Hoarder)
    def do_farmer(fx, fy, targets, crop, hand_idx=None):
        inv = private["inventories"][0] if hand_idx is None else (private["inventories"][hand_idx+1] if hand_idx+1 < len(private["inventories"]) else {})
        if sum(inv.values()) > 0:
            # Go to shed and drop
            if (fx, fy) not in [(4,4), (5,4), (4,5), (5,5)]:
                if fx < 4: return ["EAST"]
                elif fx > 5: return ["WEST"]
                elif fy < 4: return ["SOUTH"]
                elif fy > 5: return ["NORTH"]
            else:
                return ["DROP"]
                
        # Are there targets to plant?
        unplanted = []
        needs_water = []
        needs_harvest = []
        for tx, ty in targets:
            t = me["tiles"][ty][tx]
            if not isinstance(t, dict) or t.get("kind") != "PLANT":
                unplanted.append((tx, ty))
            elif isinstance(t, dict) and t.get("kind") == "PLANT":
                if t.get("yield_units", 0) > 0:
                    needs_harvest.append((tx, ty))
                elif not t.get("watered_today"):
                    needs_water.append((tx, ty))
                    
        if needs_harvest:
            tx, ty = needs_harvest[0]
            if (fx, fy) != (tx, ty):
                if fx < tx: return ["EAST"]
                elif fx > tx: return ["WEST"]
                elif fy < ty: return ["SOUTH"]
                elif fy > ty: return ["NORTH"]
            return ["HARVEST"]
            
        if needs_water:
            tx, ty = needs_water[0]
            if (fx, fy) != (tx, ty):
                if fx < tx: return ["EAST"]
                elif fx > tx: return ["WEST"]
                elif fy < ty: return ["SOUTH"]
                elif fy > ty: return ["NORTH"]
            return ["WATER"]
            
        if unplanted and private["seeds"].get(crop, 0) > 0:
            tx, ty = unplanted[0]
            if (fx, fy) != (tx, ty):
                if fx < tx: return ["EAST"]
                elif fx > tx: return ["WEST"]
                elif fy < ty: return ["SOUTH"]
                elif fy > ty: return ["NORTH"]
            return ["PLANT", crop]
            
        # Idle at shed to save time later
        if (fx, fy) not in [(4,4), (5,4), (4,5), (5,5)]:
            if fx < 4: return ["EAST"]
            elif fx > 5: return ["WEST"]
            elif fy < 4: return ["SOUTH"]
            elif fy > 5: return ["NORTH"]
            
        return ["PASS"]
        
    farmer = do_farmer(fx, fy, tomato_targets, "TOMATO", None)
    
    hands_actions = []
    for i in range(len(me["hands"])):
        if i < 4:
            hx, hy = me["hands"][i]
            hands_actions.append(do_farmer(hx, hy, hand_melon_targets[i], "MELON", i))
        else:
            hands_actions.append(["PASS"])
            
    return {"farmer": farmer, "hands": hands_actions, "market": market[:10]}
