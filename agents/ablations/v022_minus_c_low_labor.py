"""
Ablation C: V022-C minus Quad-Matched Labor (Static Low Labor: 3 workers)
"""
import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [(3, 3), (3, 2), (3, 1), (3, 0), (2, 3), (2, 2), (2, 1)]
DAY0_WHEAT = [(2, 0), (1, 3), (1, 2), (1, 1), (1, 0)]
COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1), (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2), (2, 4), (2, 3), (6, 4), (6, 3), (6, 2), (7, 4), (7, 3)
]

WEIGHT_URGENT_WATER = 1800
WEIGHT_FEED_ANIMAL = 1400
WEIGHT_CARE_ANIMAL = 1300
WEIGHT_CLEAR_WEED = 1100
WEIGHT_WATER_PLANT = 1000
WEIGHT_HARVEST_LIVESTOCK = 950
WEIGHT_COLLECT_FERTILIZER = 900
WEIGHT_HARVEST_CROP = 850
WEIGHT_BUILD_STRUCTURE = 750
WEIGHT_PLACE_ANIMAL = 700
WEIGHT_PLANT_SEED = 650

def manhattan(p1, p2): return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
def get_move_toward(c, t):
    if c[0] < t[0]: return "EAST"
    if c[0] > t[0]: return "WEST"
    if c[1] < t[1]: return "SOUTH"
    if c[1] > t[1]: return "NORTH"
    return "PASS"

def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day, hour = obs["day"], obs["hour"]
    money, tiles, unlocked_quads = me["money"], me["tiles"], me["unlocked_quadrants"]
    shed, seeds, inventories = private["shed"], private["seeds"], private["inventories"]
    market_prices = obs.get("market", {}).get("prices", {})
    all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
    num_units = len(all_units)
    
    animals_on_board, empty_structures, plants_on_board, weeds, empty_unlocked_tiles = [], [], [], [], []
    num_cows, num_sheep, num_strawberries, num_wheat_plants = 0, 0, 0, 0
    
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if t == "LOCKED": continue
            elif t is None: empty_unlocked_tiles.append((c, r))
            elif isinstance(t, dict):
                kind = t.get("kind")
                if kind == "WEED": weeds.append((c, r))
                elif kind in ["COOP", "PASTURE"]:
                    an = t.get("animal")
                    if an:
                        animals_on_board.append((c, r, an, t.get("fed_today", False), t.get("cared_today", False), t.get("fertilizer_available", False), t.get("yield_units", 0)))
                        if an == "COW": num_cows += 1
                        elif an == "SHEEP": num_sheep += 1
                    else: empty_structures.append((c, r, kind))
                elif kind == "PLANT":
                    crop = t.get("crop")
                    plants_on_board.append((c, r, crop, t.get("watered_today", False), t.get("yield_units", 0), day - t.get("planted_day", day), t.get("max_lifespan_step", 720), t.get("consecutive_unwatered", 0)))
                    if crop == "STRAWBERRY": num_strawberries += 1
                    elif crop == "WHEAT": num_wheat_plants += 1

    num_animals, num_plants = len(animals_on_board), len(plants_on_board)
    market_orders = []
    
    if day == 0 and hour == 0:
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        market_orders.append(["HIRE"])
        market_orders.append(["HIRE"])
        market_orders.append(["BUY_SEED", "MELON", 7])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 4])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
    elif day > 0:
        if hour == 0:
            # ABLATION: Static target hands = 3 throughout whole game
            target_hands = 3
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 2:
                for _ in range(target_hands - hires_today): market_orders.append(["HIRE"])
            for prod in ["FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
                if len(market_orders) >= 10: break
                p_cnt = shed.get(prod, 0)
                if p_cnt > 0: market_orders.append(["SELL", prod, min(p_cnt, 10)])
        elif hour == 1:
            current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
            target_feed = num_animals * 3 + 6 if day >= 6 else 6
            if current_wheat < target_feed and money > 40:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 4:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
            if "NE" not in unlocked_quads and money >= 1400 and day >= 6: market_orders.append(["BUY_LAND"])
            elif "SW" not in unlocked_quads and money >= 2800 and day >= 10: market_orders.append(["BUY_LAND"])
            elif "SE" not in unlocked_quads and money >= 7000 and day >= 14: market_orders.append(["BUY_LAND"])
            if day >= 6 and money >= 600 and num_animals < 15:
                if num_cows < 11 and (len(empty_structures) > 0 or shed.get("COW", 0) == 0): market_orders.append(["BUY_ANIMAL", "COW", 1])
                elif num_sheep < 4 and (len(empty_structures) > 0 or shed.get("SHEEP", 0) == 0): market_orders.append(["BUY_ANIMAL", "SHEEP", 1])
            if day >= 10 and day <= 24 and money >= 300:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if (num_strawberries + straw_seeds) < 45 and len(empty_unlocked_tiles) > 3:
                    market_orders.append(["BUY_SEED", "STRAWBERRY", min(10, 45 - (num_strawberries + straw_seeds))])
            if day >= 6 and day <= 26:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 10 and money >= 100: market_orders.append(["BUY_SEED", "WHEAT", 4])
        else:
            for prod in ["MILK", "STRAWBERRY", "WOOL", "MELON", "FERTILIZER", "CARROT", "EGG"]:
                if len(market_orders) >= 10: break
                p_cnt = shed.get(prod, 0)
                if p_cnt > 0:
                    cur_p = market_prices.get(prod, 100)
                    market_orders.append(["SELL", prod, min(p_cnt, 8 if cur_p >= 80 else 4)])

    tasks = []
    for (ax, ay, an, fed, cared, fav, yu) in animals_on_board:
        if not fed: tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
        if not cared: tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
        if yu > 0: tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
        if fav: tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
    for (px, py, crop, wat, yu, age, ml, unwat) in plants_on_board:
        is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or (crop == "MELON" and age >= 10) or (crop in ["STRAWBERRY", "TOMATO"] and yu > 0)
        if is_ripe and yu > 0: tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif not wat: tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_URGENT_WATER if unwat >= 1 else WEIGHT_WATER_PLANT, "crop": crop})
    for (wx, wy) in weeds: tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
    for (sx, sy, skind) in empty_structures:
        tgt_an = "COW" if skind == "PASTURE" and (shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict))) else ("SHEEP" if shed.get("SHEEP", 0) > 0 else None)
        if tgt_an: tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": tgt_an})
    target_pasture_count = 4 if day < 6 else (8 if day < 10 else 15)
    current_pastures = len(animals_on_board) + len(empty_structures)
    if current_pastures < target_pasture_count and money > 300 and empty_unlocked_tiles:
        cands = [pt for pt in COMPACT_PASTURE_LAYOUT if pt in empty_unlocked_tiles] or empty_unlocked_tiles
        for pt in cands[:3]: tasks.append({"type": "BUILD_PASTURE", "pos": pt, "weight": WEIGHT_BUILD_STRUCTURE})
    avail_straw, avail_wheat, avail_melon = seeds.get("STRAWBERRY", 0), seeds.get("WHEAT", 0), seeds.get("MELON", 0)
    if (avail_straw > 0 or avail_wheat > 0 or avail_melon > 0) and empty_unlocked_tiles:
        res = set(COMPACT_PASTURE_LAYOUT) if current_pastures < target_pasture_count else set()
        interior = [pt for pt in empty_unlocked_tiles if pt not in SHED_TILES and pt not in res]
        for it in interior[:25]:
            chosen = "MELON" if avail_melon > 0 and day < 5 else ("STRAWBERRY" if avail_straw > 0 and day >= 8 else "WHEAT")
            tasks.append({"type": "PLANT", "pos": it, "weight": WEIGHT_PLANT_SEED, "crop": chosen})

    pre_actions = [None] * num_units
    for u_idx, upos in enumerate(all_units):
        inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        if upos in SHED_TILES:
            if sum(v for k, v in inv.items() if k not in ["WHEAT", "SHEEP", "COW", "GOOSE"]) > 0:
                pre_actions[u_idx] = ["DROP"]
            elif empty_structures and (shed.get("COW", 0) > 0 or shed.get("SHEEP", 0) > 0) and not (inv.get("COW") or inv.get("SHEEP")):
                pre_actions[u_idx] = ["PICKUP", "COW" if shed.get("COW", 0) > 0 else "SHEEP", 1]
            elif num_animals > 0 and inv.get("WHEAT", 0) < 3 and shed.get("WHEAT", 0) > 0:
                pre_actions[u_idx] = ["PICKUP", "WHEAT", min(4, shed.get("WHEAT", 0))]

    unit_actions = []
    if day == 0:
        for u_idx, upos in enumerate(all_units):
            inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
            if u_idx == 0:
                if hour == 2 and upos in SHED_TILES and shed.get("SHEEP", 0) > 0: unit_actions.append(["PICKUP", "SHEEP", 4]); continue
                elif hour == 3 and upos in SHED_TILES and shed.get("WHEAT", 0) > 0: unit_actions.append(["PICKUP", "WHEAT", 4]); continue
                t = tiles[upos[1]][upos[0]]
                if upos in DAY0_PASTURES:
                    if t is None: unit_actions.append(["BUILD_PASTURE"]); continue
                    elif isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal"):
                        if inv.get("SHEEP", 0) > 0: unit_actions.append(["PLACE", "SHEEP"]); continue
                    elif isinstance(t, dict) and t.get("animal"):
                        if not t.get("fed_today") and inv.get("WHEAT", 0) > 0: unit_actions.append(["FEED"]); continue
                        elif not t.get("cared_today"): unit_actions.append(["CARE"]); continue
                next_p = None
                for pt in DAY0_PASTURES:
                    cur_t = tiles[pt[1]][pt[0]]
                    if cur_t is None or (isinstance(cur_t, dict) and (not cur_t.get("animal") or not cur_t.get("cared_today"))): next_p = pt; break
                unit_actions.append([get_move_toward(upos, next_p)] if next_p else ["PASS"])
            else:
                target_tile, target_crop = None, "MELON"
                for m_pos in DAY0_MELONS:
                    cur_t = tiles[m_pos[1]][m_pos[0]]
                    if (cur_t is None and seeds.get("MELON", 0) > 0) or (isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today")):
                        target_tile, target_crop = m_pos, "MELON"; break
                if not target_tile:
                    for w_pos in DAY0_WHEAT:
                        cur_t = tiles[w_pos[1]][w_pos[0]]
                        if (cur_t is None and seeds.get("WHEAT", 0) > 0) or (isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today")):
                            target_tile, target_crop = w_pos, "WHEAT"; break
                if target_tile:
                    if upos == target_tile:
                        cur_t = tiles[upos[1]][upos[0]]
                        if cur_t is None: unit_actions.append(["PLANT", target_crop])
                        elif isinstance(cur_t, dict) and cur_t.get("kind") == "PLANT" and not cur_t.get("watered_today"): unit_actions.append(["WATER"])
                        else: unit_actions.append(["PASS"])
                    else: unit_actions.append([get_move_toward(upos, target_tile)])
                else: unit_actions.append(["PASS"])
    else:
        if not tasks:
            for u_idx, upos in enumerate(all_units):
                if pre_actions[u_idx]: unit_actions.append(pre_actions[u_idx])
                elif u_idx < len(inventories) and inventories[u_idx] and upos not in SHED_TILES:
                    unit_actions.append([get_move_toward(upos, min(SHED_TILES, key=lambda s: manhattan(upos, s)))])
                elif upos in SHED_TILES and u_idx < len(inventories) and inventories[u_idx]: unit_actions.append(["DROP"])
                else: unit_actions.append(["PASS"])
        else:
            cost_matrix = []
            for u_idx, upos in enumerate(all_units):
                row = []
                inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
                inv_wheat, inv_count = inv.get("WHEAT", 0), sum(inv.values()) if isinstance(inv, dict) else 0
                for t in tasks:
                    score = t["weight"] - (manhattan(upos, t["pos"]) * 10)
                    if u_idx in [0, 1] and t["type"] in ["FEED", "CARE", "HARVEST_ANIMAL", "COLLECT_FERTILIZER", "BUILD_PASTURE", "PLACE_ANIMAL"]: score += 300
                    elif u_idx >= 2 and t["type"] in ["WATER", "HARVEST_CROP", "PLANT", "DIG"]: score += 200
                    if t["type"] == "FEED" and inv_wheat == 0: score -= 3000
                    if t["type"] == "PLACE_ANIMAL" and inv.get(t.get("animal", ""), 0) == 0: score -= 3000
                    if inv_count >= 8 and t["type"] not in ["FEED", "CARE"]: score -= 500
                    row.append(-score)
                cost_matrix.append(row)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            assignment = {r: c for r, c in zip(row_ind, col_ind)}
            for u_idx, upos in enumerate(all_units):
                if pre_actions[u_idx]: unit_actions.append(pre_actions[u_idx]); continue
                if u_idx in assignment:
                    t = tasks[assignment[u_idx]]
                    t_pos, t_type = t["pos"], t["type"]
                    inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
                    if sum(inv.values()) if isinstance(inv, dict) else 0 >= 8:
                        unit_actions.append(["DROP"] if upos in SHED_TILES else [get_move_toward(upos, min(SHED_TILES, key=lambda s: manhattan(upos, s)))])
                        continue
                    if upos == t_pos:
                        if t_type == "FEED":
                            unit_actions.append(["FEED"] if inv.get("WHEAT", 0) > 0 else (["PICKUP", "WHEAT", 4] if upos in SHED_TILES and shed.get("WHEAT", 0) > 0 else [get_move_toward(upos, min(SHED_TILES, key=lambda s: manhattan(upos, s)))]))
                        elif t_type in ["CARE", "HARVEST_ANIMAL", "COLLECT_FERTILIZER", "WATER", "HARVEST_CROP", "DIG", "BUILD_PASTURE"]:
                            act_name = "HARVEST" if t_type in ["HARVEST_ANIMAL", "HARVEST_CROP"] else t_type
                            unit_actions.append([act_name])
                        elif t_type == "PLACE_ANIMAL":
                            tan = t.get("animal", "COW")
                            unit_actions.append(["PLACE", tan] if inv.get(tan, 0) > 0 else (["PICKUP", tan, 1] if upos in SHED_TILES and shed.get(tan, 0) > 0 else [get_move_toward(upos, min(SHED_TILES, key=lambda s: manhattan(upos, s)))]))
                        elif t_type == "PLANT":
                            c_plant = t.get("crop", "WHEAT")
                            unit_actions.append(["PLANT", c_plant] if seeds.get(c_plant, 0) > 0 else ["PASS"])
                        else: unit_actions.append(["PASS"])
                    else: unit_actions.append([get_move_toward(upos, t_pos)])
                else: unit_actions.append(["PASS"])

    return {"farmer": unit_actions[0] if unit_actions else ["PASS"], "hands": unit_actions[1:] if len(unit_actions) > 1 else [], "market": market_orders[:10]}
