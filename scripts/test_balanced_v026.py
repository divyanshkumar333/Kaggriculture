import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("mod", filepath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

v026_base = load_agent("agents/v026_il_meta.py")

def agent_v026_balanced(obs):
    # Same as v026 but with cow cap 9 and strawberry cap 42
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    
    money = me["money"]
    tiles = me["tiles"]
    unlocked_quads = me["unlocked_quadrants"]
    num_quads = len(unlocked_quads)
    shed = private["shed"]
    seeds = private["seeds"]
    inventories = private["inventories"]
    market = obs.get("market", {})
    market_prices = market.get("prices", {})
    
    all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
    num_units = len(all_units)
    
    animals_on_board = []
    empty_structures = []
    plants_on_board = []
    weeds = []
    empty_unlocked_tiles = []
    
    num_cows = 0
    num_sheep = 0
    num_strawberries = 0
    num_wheat_plants = 0
    
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if t == "LOCKED":
                continue
            elif t is None:
                empty_unlocked_tiles.append((c, r))
            elif isinstance(t, dict):
                kind = t.get("kind")
                if kind == "WEED":
                    weeds.append((c, r))
                elif kind in ["COOP", "PASTURE"]:
                    an = t.get("animal")
                    if an:
                        fed = t.get("fed_today", False)
                        cared = t.get("cared_today", False)
                        fert = t.get("fertilizer_available", False)
                        yu = t.get("yield_units", 0)
                        animals_on_board.append((c, r, an, fed, cared, fert, yu))
                        if an == "COW": num_cows += 1
                        elif an == "SHEEP": num_sheep += 1
                    else:
                        empty_structures.append((c, r, kind))
                elif kind == "PLANT":
                    crop = t.get("crop")
                    wat = t.get("watered_today", False)
                    yu = t.get("yield_units", 0)
                    planted_day = t.get("planted_day", day)
                    age = day - planted_day
                    max_life = t.get("max_lifespan_step", 720)
                    unwat = t.get("consecutive_unwatered", 0)
                    plants_on_board.append((c, r, crop, wat, yu, age, max_life, unwat))
                    if crop == "STRAWBERRY": num_strawberries += 1
                    elif crop == "WHEAT": num_wheat_plants += 1

    num_animals = len(animals_on_board)
    market_orders = []
    
    if day == 0 and hour == 0:
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["BUY_ANIMAL", "COW", 1])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 3])
        market_orders.append(["BUY_SEED", "MELON", 9])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        if hour == 0:
            if day < 4:
                target_hands = 3
            elif day < 6:
                target_hands = 4 if money >= 50 else 3
            elif num_quads >= 3:
                target_hands = 12 if day >= 10 and money >= 250 else 8
            elif num_quads >= 2:
                target_hands = 7 if money >= 80 else 5
            else:
                target_hands = 4
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 2:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        if hour in [1, 6, 12, 18]:
            current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
            target_feed = num_animals * 3 + 8 if day >= 5 else 6
            if current_wheat < target_feed and money > 35:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            if "NE" not in unlocked_quads and money >= 1150 and day >= 5:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2300 and day >= 8:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # Balanced Cow Velocity: up to 9 cows
            cows_in_shed = shed.get("COW", 0)
            if day >= 3 and day <= 15 and (num_cows + cows_in_shed) < 9:
                while money >= 500 and (num_cows + cows_in_shed) < 9 and len(market_orders) < 8:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                    money -= 400
                    cows_in_shed += 1
                    
            # Strawberry Engine: Days 6 to 20, up to 42 strawberries
            if day >= 6 and day <= 20 and money >= 250:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if (num_strawberries + straw_seeds) < 42 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 42 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])
                    
            if day >= 22 and day <= 26 and money >= 100:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 35 and len(empty_unlocked_tiles) > 2:
                    market_orders.append(["BUY_SEED", "WHEAT", min(10, 35 - (num_wheat_plants + wheat_seeds))])

        for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(market_orders) >= 10: break
            p_count = shed.get(prod, 0)
            if p_count > 0:
                cur_price = market_prices.get(prod, 100)
                batch_size = 8 if cur_price >= 80 else 4
                if day >= 27: batch_size = 14
                sell_amt = min(p_count, batch_size)
                market_orders.append(["SELL", prod, sell_amt])

    # Re-use spatial Hungarian solver from V025-A
    obs["farms"][player] = me
    return v026_base.agent(obs)

a_v025 = load_agent("agents/v025_a_aggressive_cows.py")

for s in [42, 101, 202, 303, 404, 505]:
    env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
    env1.run([agent_v026_balanced, a_v025])
    m0_1 = env1.steps[-1][0]["observation"]["farms"][0]["money"]
    m1_1 = env1.steps[-1][0]["observation"]["farms"][1]["money"]
    print(f"Seed {s} | Balanced V026=${m0_1:,.0f} vs V025-A=${m1_1:,.0f} | Margin: {m0_1 - m1_1:+,.0f}")
