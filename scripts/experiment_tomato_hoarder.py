from kaggle_environments import make

def run_experiment():
    print("=== EXPERIMENT: TOMATO HOARDER vs 014_robust_trace ===")
    
    def agent_tomato_hoarder(obs):
        step = obs["step"]
        day = obs["day"]
        me = obs["farms"][obs["player"]]
        private = obs["private"]
        fx, fy = me["farmer"]
        
        market = []
        
        # Day 0: Buy 4 Tomato seeds
        if step == 0:
            market.append(["BUY_SEED", "TOMATO", 4])
            
        # On turn 718, SELL ALL TOMATOES
        if step == 718:
            tomatoes = private["shed"].get("TOMATO", 0)
            print(f"Turn 718: Shed has {tomatoes} TOMATOES")
            if tomatoes > 0:
                market.append(["SELL", "TOMATO", tomatoes])
                
        targets = [(3,4), (3,5), (4,3), (5,3)]
        
        # Are they planted?
        unplanted = []
        for tx, ty in targets:
            t = me["tiles"][ty][tx]
            if not isinstance(t, dict) or t.get("kind") != "PLANT":
                unplanted.append((tx, ty))
                
        farmer = ["PASS"]
        
        if sum(private["inventories"][0].values()) > 0:
            if (fx, fy) not in [(4,4), (5,4), (4,5), (5,5)]:
                if fx < 4: farmer = ["EAST"]
                elif fx > 4: farmer = ["WEST"]
                elif fy < 4: farmer = ["SOUTH"]
                elif fy > 4: farmer = ["NORTH"]
            else:
                farmer = ["DROP"]
        else:
            needs_harvest = []
            needs_water = []
            for tx, ty in targets:
                t = me["tiles"][ty][tx]
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    if t.get("yield_units", 0) > 0:
                        needs_harvest.append((tx, ty))
                    if not t.get("watered_today"):
                        needs_water.append((tx, ty))
                        
            if needs_harvest:
                tx, ty = needs_harvest[0]
                if (fx, fy) != (tx, ty):
                    if fx < tx: farmer = ["EAST"]
                    elif fx > tx: farmer = ["WEST"]
                    elif fy < ty: farmer = ["SOUTH"]
                    elif fy > ty: farmer = ["NORTH"]
                else:
                    farmer = ["HARVEST"]
            elif needs_water:
                tx, ty = needs_water[0]
                if (fx, fy) != (tx, ty):
                    if fx < tx: farmer = ["EAST"]
                    elif fx > tx: farmer = ["WEST"]
                    elif fy < ty: farmer = ["SOUTH"]
                    elif fy > ty: farmer = ["NORTH"]
                else:
                    farmer = ["WATER"]
            elif unplanted and private["seeds"].get("TOMATO", 0) > 0:
                tx, ty = unplanted[0]
                if (fx, fy) != (tx, ty):
                    if fx < tx: farmer = ["EAST"]
                    elif fx > tx: farmer = ["WEST"]
                    elif fy < ty: farmer = ["SOUTH"]
                    elif fy > ty: farmer = ["NORTH"]
                else:
                    farmer = ["PLANT", "TOMATO"]
                    
        return {"farmer": farmer, "market": market}
        
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run([agent_tomato_hoarder, "agents/014_robust_trace.py"])
    
    final_step = env.steps[-1]
    obs = final_step[0].observation
    print(f"P0 (Tomato Hoarder) Money: {obs['farms'][0]['money']}")
    print(f"P1 (014 Robust Trace) Money: {obs['farms'][1]['money']}")
    print(f"Final TOMATO Price: {obs['market']['prices']['TOMATO']}")
    print(f"Final TOMATO Inventory: {obs['market']['inventory']['TOMATO']}")

if __name__ == "__main__":
    run_experiment()
