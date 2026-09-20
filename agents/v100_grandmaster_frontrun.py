"""
Candidate V100: V085 Grandmaster Execution + V052 Front-Run Market Overlay
--------------------------------------------------------------------------
Hypothesis EXP-035: The main.py trace is locked to a single game.
Against strong opponents, a real-time executor with the same market intelligence
should be more robust across seeds.

Architecture:
- V085 two-phase macro (cow engine -> expand/diversify)
- Real-time Hungarian task dispatch
- V052 opponent-shed inference from main.py
- Front-run + repay + impact-ranking from main.py
- Town demand awareness
- NO trace dependency

Expected improvement over V085: better market timing via front-run
Expected improvement over main.py: not seed-locked, better vs novel opponents
"""
import copy, math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
COMPACT_PASTURE = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3),
    (6, 4), (6, 3), (6, 2),
    (7, 4), (7, 3),
]
DAY0_WHEAT = [(2, 0), (1, 3), (1, 2), (1, 1), (1, 0)]

WEIGHTS = {
    "WATER_CRITICAL": 2000, "FEED_CRITICAL": 1900, "CARE": 1600,
    "FEED_NORMAL": 1500,    "HARVEST_CROP": 1200, "HARVEST_ANIMAL": 1100,
    "FERTILIZE": 1050,      "WATER_NORMAL": 1000, "COLLECT_FERT": 950,
    "PLANT": 900,           "BUILD": 800,         "PLACE": 750,
    "DIG_WEED": 700,
}
_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_MARKET_PARAMS = {
    "MELON":       {"base": 250, "I0": 10000, "T": 300, "bf": "log",   "bt": 0.20, "af": "sq",     "at": 3.60},
    "MILK":        {"base": 160, "I0": 10000, "T": 122, "bf": "sqrt",  "bt": 0.60, "af": "linear", "at": 1.60},
    "STRAWBERRY":  {"base": 120, "I0": 10000, "T": 100, "bf": "sqrt",  "bt": 0.70, "af": "linear", "at": 1.60},
    "WOOL":        {"base": 200, "I0": 10000, "T": 105, "bf": "log",   "bt": 0.20, "af": "sq",     "at": 3.20},
}
_FR_STATE = {
    0: {"last_step": -1, "due": {}, "prev_inv": {}, "last_action": None,
        "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}},
    1: {"last_step": -1, "due": {}, "prev_inv": {}, "last_action": None,
        "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}},
}

def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def move_toward(cur, tgt):
    cx, cy = cur; tx, ty = tgt
    if cx < tx: return "EAST"
    if cx > tx: return "WEST"
    if cy < ty: return "SOUTH"
    if cy > ty: return "NORTH"
    return "PASS"

def _shape(f, x, T=None):
    x = max(0.0, float(x))
    if f == "linear": return x
    if f == "sq":     return x * x
    if f == "sqrt":   return math.sqrt(x)
    if f == "log":    return math.log(1.0 + x)
    return x

def _mkt_price(item, inv):
    p = _MARKET_PARAMS.get(item)
    if not p: return 1
    base, I0, T = p["base"], p["I0"], p["T"]
    if inv < I0:
        amp = p["bt"] * base / _shape(p["bf"], T, T)
        price = base + amp * _shape(p["bf"], I0 - inv, T)
    else:
        amp = p["at"] * base / _shape(p["af"], T, T)
        price = base - amp * _shape(p["af"], inv - I0, T)
    return max(1, int(round(price)))

def _town_demand(obs, item, step):
    d = 1 if item != "FERTILIZER" and step % 24 == 0 else 0
    if step % 4 != 0: return d
    for shop in (obs.get("town") or {}).get("unlocked_shops", []):
        prods = _SHOP_PRODUCTS.get(shop, ())
        if item in prods: d += 2 if len(prods) == 1 else 1
    return d

def _update_state(obs, step):
    seat = obs["player"]
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due": {}, "prev_inv": {}, "last_action": None,
                 "opp_shed": {}, "opp_plants": {}, "opp_animals": {}, "macro": {"phase": 1}}
        _FR_STATE[seat] = state

    opp_idx = 1 - seat
    farms = obs.get("farms", [])
    opp_farm = farms[opp_idx] if len(farms) > opp_idx else {}
    prev_plants = state.setdefault("opp_plants", {})
    prev_animals = state.setdefault("opp_animals", {})
    curr_plants = {}; curr_animals = {}

    for y, row in enumerate(opp_farm.get("tiles", [])):
        for x, tile in enumerate(row or []):
            if not isinstance(tile, dict): continue
            k = tile.get("kind")
            if k == "PLANT":
                curr_plants[(x, y)] = {"crop": str(tile.get("crop", "")),
                                        "yu": int(tile.get("yield_units", 0) or 0)}
            elif k in ("COOP", "PASTURE") and "animal" in tile:
                curr_animals[(x, y)] = {"animal": str(tile.get("animal", "")),
                                         "yu": int(tile.get("yield_units", 0) or 0)}

    opp_shed = state.setdefault("opp_shed", {})
    for pos, prev in prev_plants.items():
        curr = curr_plants.get(pos)
        h = prev["yu"] if (curr is None and prev["yu"] > 0) else \
            (prev["yu"] - curr["yu"] if curr and curr["crop"] == prev["crop"] and curr["yu"] < prev["yu"] else 0)
        if h > 0: opp_shed[prev["crop"]] = opp_shed.get(prev["crop"], 0) + h
    for pos, prev in prev_animals.items():
        curr = curr_animals.get(pos)
        h = prev["yu"] - curr["yu"] if (curr and curr["animal"] == prev["animal"] and curr["yu"] < prev["yu"]) else 0
        if h > 0:
            item = "EGG" if prev["animal"] == "GOOSE" else "MILK" if prev["animal"] == "COW" else "WOOL"
            opp_shed[item] = opp_shed.get(item, 0) + h

    mkt_inv = obs.get("market", {}).get("inventory", {})
    prev_inv = state.get("prev_inv", {})
    last_action = state.get("last_action") or {}
    our_sales = {}
    for o in (last_action.get("market") or []):
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
            our_sales[str(o[1])] = our_sales.get(str(o[1]), 0) + max(0, int(o[2]))
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        opp_s = max(0, int(mkt_inv.get(item, 10000)) - int(prev_inv.get(item, 10000)) - our_sales.get(item, 0))
        if opp_s > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - opp_s)
        d = _town_demand(obs, item, step)
        if d > 0: opp_shed[item] = max(0, opp_shed.get(item, 0) - d)

    state["opp_plants"] = curr_plants
    state["opp_animals"] = curr_animals
    state["prev_inv"] = dict(mkt_inv)
    state["last_step"] = step
    return state

def _front_run(action, obs, state, step, shed):
    """Front-run opponent's anticipated sells using inferred opp_shed."""
    opp_shed = state.get("opp_shed", {})
    due_map = state.setdefault("due", {})
    market = list(action.get("market") or [])
    items = ("MELON", "MILK", "STRAWBERRY", "WOOL")
    for item in items:
        if len(market) >= 10: break
        opp_qty = opp_shed.get(item, 0)
        if opp_qty < 2: continue
        if _town_demand(obs, item, step) > 0: continue
        stock = max(0, int((shed or {}).get(item, 0)))
        target_step = step + 1
        existing_sell = sum(max(0, int(o[2])) for o in market
                           if len(o) >= 3 and o[0] == "SELL" and o[1] == item)
        qty = min(opp_qty, max(0, stock - existing_sell))
        if qty <= 0: continue
        existing = next((o for o in market if len(o) >= 3 and o[0] == "SELL" and o[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + qty
        else:
            market.append(["SELL", item, qty])
        due_map.setdefault(target_step, {})[item] = due_map.get(target_step, {}).get(item, 0) + qty
    action["market"] = market[:10]
    return action

def _repay(action, state, step):
    due_map = state.get("due", {})
    if step not in due_map: return action
    due = {str(k): max(0, int(v)) for k, v in dict(due_map[step]).items()}
    market = []
    for raw in (action.get("market") or []):
        o = list(raw)
        if len(o) >= 3 and o[0] == "SELL" and o[1] in due and due[o[1]] > 0:
            req = max(0, int(o[2]))
            red = min(req, due[o[1]])
            req -= red; due[o[1]] -= red
            if req <= 0: continue
            o[2] = req
        market.append(o)
    action["market"] = market[:10]
    del due_map[step]
    return action

def _impact_rank(obs, action):
    market = list(action.get("market") or [])
    sells = [(i, o) for i, o in enumerate(market)
             if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL"]
    if len(sells) < 2: return action
    mkt_inv = obs.get("market", {}).get("inventory", {})
    prices = obs.get("market", {}).get("prices", {})
    scored = []
    for idx, o in sells:
        item = str(o[1])
        qty = max(0, int(o[2]))
        inv = int(mkt_inv.get(item, 10000) or 0)
        cur_p = float(prices.get(item, _mkt_price(item, inv)) or 0)
        lat_p = float(_mkt_price(item, inv + qty))
        scored.append((float(qty) * max(0.0, cur_p - lat_p), -idx, idx, list(o)))
    scored.sort(reverse=True)
    new_market = list(market)
    sell_indices = [x[2] for x in sorted([(s[1], s[2]) for s in scored])]
    ranked = [s[3] for s in scored]
    for new_idx, (orig_idx, ranked_o) in enumerate(zip(sell_indices, ranked)):
        new_market[orig_idx] = ranked_o
    action["market"] = new_market
    return action

def agent(obs):
    try:
        player = obs["player"]
        me = obs["farms"][player]
        private = obs["private"]
        day, hour, step = obs["day"], obs["hour"], obs["step"]
        state = _update_state(obs, step)
        macro = state["macro"]

        money = me["money"]
        tiles = me["tiles"]
        shed = private["shed"]
        seeds = private["seeds"]
        inventories = private["inventories"]
        market_prices = obs.get("market", {}).get("prices", {})
        unlocked = me["unlocked_quadrants"]

        all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
        num_units = len(all_units)
        market_orders = []

        # ----------------------------------------------------------------
        # MACRO STRATEGY (Phase-based)
        # ----------------------------------------------------------------
        if day == 0 and hour == 0:
            # Aggressive opening: secure wheat feed, hire workers, buy 2 cows, plant wheat
            market_orders.append(["BUY_PRODUCT", "WHEAT", 34])
            for _ in range(9): market_orders.append(["HIRE"])
            market_orders.append(["BUY_ANIMAL", "COW", 2])
            market_orders.append(["BUY_SEED", "WHEAT", 5])
            macro["phase"] = 1

        elif day > 0:
            if hour == 0:
                hires = me.get("hires_today", 0)
                target_h = 11 if macro["phase"] == 1 else 14
                if hires < target_h and money >= 5:
                    for _ in range(min(target_h - hires, 10)):
                        market_orders.append(["HIRE"])
                # Sell fertilizer
                fert = shed.get("FERTILIZER", 0)
                if fert > 0 and len(market_orders) < 10:
                    market_orders.append(["SELL", "FERTILIZER", min(fert, 10)])

            if hour in (1, 6, 12, 18):
                num_cows = sum(1 for r in tiles for t in r
                               if isinstance(t, dict) and t.get("animal") == "COW")
                total_cows = num_cows + shed.get("COW", 0)

                # Phase transition
                if day >= 10 or total_cows >= 10:
                    macro["phase"] = 2

                # Feed reserves
                current_wheat = shed.get("WHEAT", 0) + sum(
                    inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
                target_feed = max(num_cows * 3 + 5, 10)
                if current_wheat < target_feed and money > 35 and len(market_orders) < 8:
                    market_orders.append(["BUY_PRODUCT", "WHEAT",
                                          min(target_feed - current_wheat, 10)])

                # Land expansion
                if "NE" not in unlocked and money >= 1200 and len(market_orders) < 9:
                    market_orders.append(["BUY_LAND"])
                elif "SW" not in unlocked and money >= 2500 and day >= 8 and len(market_orders) < 9:
                    market_orders.append(["BUY_LAND"])

                if macro["phase"] == 1:
                    # Cow accumulation
                    if total_cows < 12 and money >= 400 and len(market_orders) < 9:
                        market_orders.append(["BUY_ANIMAL", "COW", 1])
                    # Wheat seeds for feed
                    if seeds.get("WHEAT", 0) < 5 and money >= 10 and len(market_orders) < 9:
                        market_orders.append(["BUY_SEED", "WHEAT", 5])
                else:
                    # Phase 2: diversify
                    if seeds.get("STRAWBERRY", 0) < 10 and money >= 250 and len(market_orders) < 8:
                        market_orders.append(["BUY_SEED", "STRAWBERRY", 10])
                    if day >= 15 and seeds.get("MELON", 0) < 5 and money >= 300 and len(market_orders) < 9:
                        market_orders.append(["BUY_SEED", "MELON", 5])

            # Paced selling with opponent shed awareness
            opp_shed = state.get("opp_shed", {})
            for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "EGG", "WHEAT"]:
                if len(market_orders) >= 10: break
                p_count = shed.get(prod, 0)
                if p_count <= 0: continue
                cur_price = market_prices.get(prod, 100)
                # Sell aggressively if opponent has inventory (front-run their sell)
                if opp_shed.get(prod, 0) >= 2 or cur_price >= 80 or day >= 27:
                    batch = 12 if day >= 27 else 8
                    market_orders.append(["SELL", prod, min(p_count, batch)])

        # Apply front-run, repay, and impact ranking
        action = {"farmer": ["PASS"], "hands": [["PASS"]] * (num_units - 1),
                  "market": market_orders[:10]}
        action = _repay(action, state, step)
        action = _front_run(action, obs, state, step, shed)
        action = _impact_rank(obs, action)

        # ----------------------------------------------------------------
        # MICRO: TASK GENERATION + HUNGARIAN DISPATCH
        # ----------------------------------------------------------------
        animals_on_board = []
        empty_structures = []
        plants_on_board = []
        weeds = []
        empty_unlocked = []

        for r in range(10):
            for c in range(10):
                t = tiles[r][c]
                if t == "LOCKED": continue
                if t is None:
                    empty_unlocked.append((c, r))
                elif isinstance(t, dict):
                    k = t.get("kind")
                    if k == "WEED":
                        weeds.append((c, r))
                    elif k in ("COOP", "PASTURE"):
                        an = t.get("animal")
                        if an:
                            animals_on_board.append({
                                "pos": (c, r), "animal": an,
                                "fed": t.get("fed_today", False),
                                "cared": t.get("cared_today", False),
                                "fert_av": t.get("fertilizer_available", False),
                                "yu": t.get("yield_units", 0),
                            })
                        else:
                            empty_structures.append({"pos": (c, r), "kind": k})
                    elif k == "PLANT":
                        plants_on_board.append({
                            "pos": (c, r),
                            "crop": t.get("crop"),
                            "watered": t.get("watered_today", False),
                            "yu": t.get("yield_units", 0),
                            "age": day - t.get("planted_day", day),
                            "unwat": t.get("consecutive_unwatered", 0),
                        })

        tasks = []
        for a in animals_on_board:
            if not a["fed"]:
                tasks.append({"type": "FEED", "pos": a["pos"],
                               "weight": WEIGHTS["FEED_CRITICAL"], "animal": a["animal"]})
            if not a["cared"]:
                tasks.append({"type": "CARE", "pos": a["pos"],
                               "weight": WEIGHTS["CARE"], "animal": a["animal"]})
            if a["yu"] > 0:
                tasks.append({"type": "HARVEST_ANIMAL", "pos": a["pos"],
                               "weight": WEIGHTS["HARVEST_ANIMAL"]})
            if a["fert_av"]:
                tasks.append({"type": "COLLECT_FERT", "pos": a["pos"],
                               "weight": WEIGHTS["COLLECT_FERT"]})

        for p in plants_on_board:
            crop, age, yu, watered, unwat = p["crop"], p["age"], p["yu"], p["watered"], p["unwat"]
            ripe = ((crop in ("WHEAT", "CARROT") and age >= 2) or
                    (crop == "MELON" and age >= 10) or
                    (crop in ("STRAWBERRY", "TOMATO") and yu > 0))
            if ripe and yu > 0:
                tasks.append({"type": "HARVEST_CROP", "pos": p["pos"],
                               "weight": WEIGHTS["HARVEST_CROP"], "crop": crop})
            elif not watered:
                w = WEIGHTS["WATER_CRITICAL"] if unwat >= 1 else WEIGHTS["WATER_NORMAL"]
                tasks.append({"type": "WATER", "pos": p["pos"], "weight": w, "crop": crop})

        for w in weeds:
            tasks.append({"type": "DIG_WEED", "pos": w, "weight": WEIGHTS["DIG_WEED"]})

        for s in empty_structures:
            target = None
            if s["kind"] == "PASTURE":
                if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories
                                                   if isinstance(inv, dict)):
                    target = "COW"
                elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories
                                                      if isinstance(inv, dict)):
                    target = "SHEEP"
            if target:
                tasks.append({"type": "PLACE", "pos": s["pos"],
                               "weight": WEIGHTS["PLACE"], "animal": target})

        # Build pastures where needed
        pasture_set = set(COMPACT_PASTURE)
        total_structs = len(animals_on_board) + len(empty_structures)
        desired_pastures = min(14, len(animals_on_board) + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
        for p in COMPACT_PASTURE:
            if total_structs >= desired_pastures: break
            if p[0] >= 5 and "NE" not in unlocked: continue
            if p[1] >= 5 and "SW" not in unlocked: continue
            if tiles[p[1]][p[0]] is None:
                tasks.append({"type": "BUILD", "pos": p, "weight": WEIGHTS["BUILD"]})
                total_structs += 1

        # Plant seeds in open tiles
        avail_straw = seeds.get("STRAWBERRY", 0)
        avail_wheat = seeds.get("WHEAT", 0)
        for ep in empty_unlocked:
            if ep in pasture_set: continue
            if avail_straw > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHTS["PLANT"],
                               "crop": "STRAWBERRY"})
                avail_straw -= 1
            elif avail_wheat > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHTS["PLANT"],
                               "crop": "WHEAT"})
                avail_wheat -= 1

        if not tasks:
            action["farmer"] = ["PASS"]
            action["hands"] = [["PASS"]] * (num_units - 1)
            state["last_action"] = copy.deepcopy(action)
            return action

        # Hungarian matching
        cost_matrix = []
        for u_idx, u_pos in enumerate(all_units):
            u_inv = (inventories[u_idx] if u_idx < len(inventories)
                     and isinstance(inventories[u_idx], dict) else {})
            costs = []
            for t in tasks:
                dist = manhattan(u_pos, t["pos"])
                pen = 0
                if t["type"] == "FEED" and u_inv.get("WHEAT", 0) == 0:
                    pen = min(manhattan(u_pos, sp) for sp in SHED_TILES) + 8
                elif t["type"] == "PLACE" and u_inv.get(t.get("animal", ""), 0) == 0:
                    pen = min(manhattan(u_pos, sp) for sp in SHED_TILES) + 8
                costs.append((2000 - t["weight"]) + dist * 12 + pen)
            cost_matrix.append(costs)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assigned = {r: tasks[c] for r, c in zip(row_ind, col_ind)}

        unit_actions = []
        for u_idx, u_pos in enumerate(all_units):
            u_inv = (inventories[u_idx] if u_idx < len(inventories)
                     and isinstance(inventories[u_idx], dict) else {})

            # Drop sellable inventory when adjacent to shed
            carried = sum(u_inv.get(p, 0) for p in
                          ["MILK", "WOOL", "STRAWBERRY", "MELON", "FERTILIZER", "CARROT", "EGG"])
            if u_pos in SHED_TILES and carried >= 3:
                unit_actions.append(["DROP"])
                continue

            if u_idx not in assigned:
                nearest_shed = min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp))
                unit_actions.append([move_toward(u_pos, nearest_shed)])
                continue

            t = assigned[u_idx]
            t_pos, t_type = t["pos"], t["type"]

            if t_type == "FEED":
                if u_inv.get("WHEAT", 0) == 0:
                    if u_pos in SHED_TILES: unit_actions.append(["PICKUP", "WHEAT", 4])
                    else: unit_actions.append([move_toward(u_pos, min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp)))])
                elif u_pos == t_pos: unit_actions.append(["FEED"])
                else: unit_actions.append([move_toward(u_pos, t_pos)])
            elif t_type == "PLACE":
                an = t["animal"]
                if u_inv.get(an, 0) == 0:
                    if u_pos in SHED_TILES: unit_actions.append(["PICKUP", an, 1])
                    else: unit_actions.append([move_toward(u_pos, min(SHED_TILES, key=lambda sp: manhattan(u_pos, sp)))])
                elif u_pos == t_pos: unit_actions.append(["PLACE", an, 1])
                else: unit_actions.append([move_toward(u_pos, t_pos)])
            else:
                if u_pos != t_pos:
                    unit_actions.append([move_toward(u_pos, t_pos)])
                else:
                    dispatch = {
                        "CARE": ["CARE"], "HARVEST_ANIMAL": ["HARVEST"],
                        "COLLECT_FERT": ["COLLECT_FERTILIZER"], "WATER": ["WATER"],
                        "HARVEST_CROP": ["HARVEST"], "DIG_WEED": ["DIG"],
                        "BUILD": ["BUILD_PASTURE"],
                        "PLANT": ["PLANT", t.get("crop", "WHEAT")],
                    }
                    unit_actions.append(dispatch.get(t_type, ["PASS"]))

        action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
        action["hands"] = unit_actions[1:] if len(unit_actions) > 1 else []

        # Align hands length
        expected_hands = num_units - 1
        while len(action["hands"]) < expected_hands:
            action["hands"].append(["PASS"])
        action["hands"] = action["hands"][:expected_hands]

        state["last_action"] = copy.deepcopy(action)
        return action

    except Exception:
        import traceback; traceback.print_exc()
        farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
        return {"farmer": ["PASS"],
                "hands": [["PASS"] for _ in (farm.get("hands") or [])],
                "market": []}
