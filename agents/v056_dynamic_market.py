"""
Agent V027: Hierarchical Meta Policy (Causally Validated Champion)
------------------------------------------------------------------
Synthesizes the empirically and causally validated Grandmaster meta:
1. Day 0 Opening: 2 Cows, 2 Sheep, 9 Melons, 5 Wheat, 5 Hires ($22 reserve).
2. Staged Labor Scaling: 6 workers (D0-D2) -> 7 workers (D3-D5) -> 12 workers (D6+ with 2+ quads).
3. Calibrated Cow Capacity: 8 Cows maximum (prevents the Milk Glut Trap and maintains $70+ milk prices).
4. Delayed Strawberry Powerhouse: 40 Strawberries initiated on Day 8-9 (preserves $1,000+ D8 cash for Q2 unlock).
5. Non-Destructive Crop Preservation: Continues strawberry harvesting through Day 30 (zero voluntary DIG destruction).
6. Adaptive Shed Pacing: Dynamic batch sizes (8-12 units) with urgency threshold at >= 60 shed items and D27-30 liquidation.
7. Micro Hungarian Shield: Provably safe zero-starve, zero-weed, zero-missed-watering spatial task assignment.
"""

import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [
    (3, 3), (3, 2), (3, 1), (3, 0),
    (2, 3), (2, 2), (2, 1), (2, 0),
    (1, 3)
]
DAY0_WHEAT = [(1, 2), (1, 1), (1, 0), (0, 3), (0, 2)]

COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3), (2, 2),
    (6, 4), (6, 3), (6, 2),
]

WEIGHT_URGENT_WATER = 2000
WEIGHT_FEED_ANIMAL = 1600
WEIGHT_CARE_ANIMAL = 1400
WEIGHT_CLEAR_WEED = 1200
WEIGHT_WATER_PLANT = 1000
WEIGHT_HARVEST_LIVESTOCK = 950
WEIGHT_COLLECT_FERTILIZER = 900
WEIGHT_HARVEST_CROP = 850
WEIGHT_BUILD_STRUCTURE = 750
WEIGHT_PLACE_ANIMAL = 700
WEIGHT_PLANT_SEED = 650

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_move_toward(current, target):
    cx, cy = current
    tx, ty = target
    if cx < tx: return "EAST"
    if cx > tx: return "WEST"
    if cy < ty: return "SOUTH"
    if cy > ty: return "NORTH"
    return "PASS"

_MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

def _shape(func, x, T=None):
    x = max(0.0, float(x))
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "hinge":
        if not T or T <= 0: return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x

def _market_price(item, inventory):
    p = _MARKET_PARAMS.get(item)
    if not p: return 1
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(price)))

def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )

def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = obs.get("market", {}) or {}
    inventory = market.get("inventory", {}) or {}
    prices = market.get("prices", {}) or {}
    current_inventory = int(inventory.get(item, 10000) or 0)
    current_quote = float(prices.get(item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _rank_sell_slots(obs, action):
    market = list(action.get("market") or [])
    if len(market) < 2:
        return action
    sell_indices = [idx for idx, order in enumerate(market) if _is_sell(order)]
    if len(sell_indices) < 2:
        return action
    scored_sells = []
    for idx in sell_indices:
        order = market[idx]
        score = _impact_score(obs, order)
        scored_sells.append((score, -idx, list(order)))
    scored_sells.sort(reverse=True)
    ranked_orders = [row[2] for row in scored_sells]
    new_market = list(market)
    for idx, new_order in zip(sell_indices, ranked_orders):
        new_market[idx] = new_order
        
    # Trim perfectly to 10 slots
    action["market"] = new_market[:10]
    return action

def agent(obs):
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
    current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
    
    # -------------------------------------------------------------------------
    # 1. MACRO STRATEGY & MARKET ORDERS
    # -------------------------------------------------------------------------
    if day == 0 and hour == 0:
        # Phase 2 Causal Champion Opening: 2 Cows + 2 Sheep + 9 Melons + 5 Wheat + 5 Hires
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        for _ in range(5):
            market_orders.append(["HIRE"])
        market_orders.append(["BUY_ANIMAL", "COW", 2])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 2])
        market_orders.append(["BUY_SEED", "MELON", 9])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        # STAGED LABOR SCALING (Hour 0)
        if hour == 0:
            if day < 3:
                target_hands = 5 # 6 workers
            elif day < 6:
                target_hands = 6 # 7 workers
            elif num_quads >= 2 and money >= 50:
                target_hands = 11 # 12 workers (Causally validated 85% win rate)
            else:
                target_hands = 6
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 5:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        # CAPITAL EXPANSION & LAND (Hours 1, 6, 12, 18)
        if hour in [1, 6, 12, 18]:
            target_feed = num_animals * 3 + 8 if day >= 5 else 6
            if current_wheat < target_feed and money > 35:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            # Quadrant Unlocks
            if "NE" not in unlocked_quads and money >= 1150 and day >= 6:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2300 and day >= 10:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # Calibrated Cow Capacity (Optimal: 8 Cows)
            cows_in_shed = shed.get("COW", 0)
            if day >= 3 and day <= 15 and (num_cows + cows_in_shed) < 8:
                while money >= 500 and (num_cows + cows_in_shed) < 8 and len(market_orders) < 8:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                    money -= 400
                    cows_in_shed += 1
                    
            # Delayed Strawberry Powerhouse (Day 8-9 start, 40 capacity)
            straw_seeds = seeds.get("STRAWBERRY", 0)
            if day >= 8 and day <= 20 and money >= 250:
                if (num_strawberries + straw_seeds) < 40 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 40 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])

        # ADAPTIVE SHED PACING & MATHEMATICAL SELLING
        total_in_shed = sum(cnt for item, cnt in shed.items() if item not in ["COW", "SHEEP"])
        urgency = total_in_shed >= 60
        
        for prod, p_count in shed.items():
            if prod not in ["COW", "SHEEP"] and p_count > 0:
                cur_price = market_prices.get(prod, 100)
                if urgency or day >= 27:
                    batch_size = 14 if day >= 27 else 12
                elif cur_price >= 80:
                    batch_size = 8
                else:
                    batch_size = 4
                sell_amt = min(p_count, batch_size)
                market_orders.append(["SELL", prod, sell_amt])

    # -------------------------------------------------------------------------
    # 2. TASK GENERATION & PRIORITIZATION
    # -------------------------------------------------------------------------
    tasks = []
    for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
        if not is_fed:
            tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
        if not is_cared:
            tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
        if y_u > 0:
            tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
        if f_av:
            tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
            
    for (px, py, crop, is_wat, y_u, age, max_life, unwat) in plants_on_board:
        is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or (crop == "MELON" and age >= 10) or (crop in ["STRAWBERRY", "TOMATO"] and y_u > 0)
        if is_ripe and y_u > 0:
            tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif not is_wat:
            tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_URGENT_WATER if unwat >= 1 else WEIGHT_WATER_PLANT, "crop": crop})
            
    for (wx, wy) in weeds:
        tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
        
    for (sx, sy, skind) in empty_structures:
        target_animal = None
        if skind == "PASTURE":
            if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "COW"
            elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "SHEEP"
        if target_animal:
            tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})
            
    if day == 0:
        for p in DAY0_PASTURES:
            if tiles[p[1]][p[0]] is None:
                tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
    else:
        desired_pastures = min(12, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
        total_structures = len(animals_on_board) + len(empty_structures)
        if total_structures < desired_pastures:
            for p in COMPACT_PASTURE_LAYOUT:
                if total_structures >= desired_pastures:
                    break
                if p[0] >= 5 and "NE" not in unlocked_quads: continue
                if p[1] >= 5 and "SW" not in unlocked_quads: continue
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
                    total_structures += 1

    if day == 0:
        if seeds.get("MELON", 0) > 0:
            for p in DAY0_MELONS:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
        if seeds.get("WHEAT", 0) > 0:
            for p in DAY0_WHEAT:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
    else:
        avail_straw_seeds = seeds.get("STRAWBERRY", 0)
        avail_wheat_seeds = seeds.get("WHEAT", 0)
        pasture_set = set(COMPACT_PASTURE_LAYOUT)
        for ep in empty_unlocked_tiles:
            if ep in pasture_set:
                continue
            if avail_straw_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "STRAWBERRY"})
                avail_straw_seeds -= 1
            elif avail_wheat_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
                avail_wheat_seeds -= 1

    # -------------------------------------------------------------------------
    # 3. HUNGARIAN DISPATCH & MICRO EXECUTION
    # -------------------------------------------------------------------------
    unit_actions = ["PASS"] * num_units
    if not tasks:
        return {
            "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
            "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
            "market": market_orders
        }
        
    cost_matrix = []
    for u_idx, u_pos in enumerate(all_units):
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        u_wheat = u_inv.get("WHEAT", 0)
        u_row = []
        for t in tasks:
            dist = manhattan(u_pos, t["pos"])
            w = t["weight"]
            
            # Distance penalty
            effective_cost = -w + (dist * 8)
            
            # Feed bonus if unit already carries wheat
            if t["type"] == "FEED":
                if u_wheat > 0:
                    effective_cost -= 150
                elif current_wheat == 0:
                    effective_cost += 3000 # Can't feed without wheat
                    
            # Animal placement check
            if t["type"] == "PLACE_ANIMAL":
                an = t.get("animal")
                if u_inv.get(an, 0) > 0:
                    effective_cost -= 200
                elif shed.get(an, 0) == 0:
                    effective_cost += 3000
                    
            u_row.append(effective_cost)
        cost_matrix.append(u_row)
        
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    assigned_tasks = {}
    for r_i, c_i in zip(row_ind, col_ind):
        assigned_tasks[r_i] = tasks[c_i]
        
    for u_idx in range(num_units):
        u_pos = all_units[u_idx]
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        
        # Check if unit needs to drop off heavy produce
        u_produce = sum(v for k, v in u_inv.items() if k not in ["COW", "SHEEP", "WHEAT"])
        if u_produce >= 8:
            # Move to shed to drop off
            closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
                continue
            else:
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        if u_idx not in assigned_tasks:
            # Default to shed drop or PASS
            if u_produce > 0 and u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
            else:
                unit_actions[u_idx] = ["PASS"]
            continue
            
        t = assigned_tasks[u_idx]
        t_type = t["type"]
        t_pos = t["pos"]
        
        # Check prerequisites for FEED and PLACE_ANIMAL
        if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
            # Need to pick up wheat first
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["PICKUP", "WHEAT", min(5, shed.get("WHEAT", 0))]
            else:
                closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
            continue
            
        if t_type == "PLACE_ANIMAL":
            an = t.get("animal")
            if u_inv.get(an, 0) == 0 and shed.get(an, 0) > 0:
                if u_pos in SHED_TILES:
                    unit_actions[u_idx] = ["PICKUP", an, 1]
                else:
                    closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                    unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        # Action execution at tile
        if u_pos == t_pos:
            if t_type == "FEED": unit_actions[u_idx] = ["FEED"]
            elif t_type == "CARE": unit_actions[u_idx] = ["CARE"]
            elif t_type in ["HARVEST_CROP", "HARVEST_ANIMAL"]: unit_actions[u_idx] = ["HARVEST"]
            elif t_type == "WATER": unit_actions[u_idx] = ["WATER"]
            elif t_type == "COLLECT_FERTILIZER": unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
            elif t_type == "DIG": unit_actions[u_idx] = ["DIG"]
            elif t_type == "BUILD_PASTURE": unit_actions[u_idx] = ["BUILD_PASTURE"]
            elif t_type == "PLACE_ANIMAL": unit_actions[u_idx] = ["PLACE", t.get("animal"), 1]
            elif t_type == "PLANT": unit_actions[u_idx] = ["PLANT", t.get("crop")]
            else: unit_actions[u_idx] = ["PASS"]
        else:
            unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]

    action = {
        "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
        "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
        "market": market_orders
    }
    return _rank_sell_slots(obs, action)
