"""
v090_meta_adaptive.py — Replay-Derived Cow+Sheep+Melon Strategy

EVIDENCE:
Two top replays (156k, 151k final cash) show IDENTICAL openings.
The strategy: 1 Cow + 4 Sheep + Melon seeds, with risk-free wheat exploit.
Micro: All 5 animals clustered near shed center, placed by Day 1.

KEY DIFFERENCES from our previous agents:
1. Risk-free wheat exploit on Hour 0 (not Hour 1)
2. Pastures at shed-center tiles (3,2)-(4,4), not random tiles
3. All animals placed in Day 0 Hours 4-12 using hands
4. Fertilizer (from 5 animals) sold daily = primary income
5. Animals never die because they're all adjacent to shed wheat
"""
from scipy.optimize import linear_sum_assignment

SHED_ADJ = {(4,4), (5,4), (4,5), (5,5)}
# Pasture zone: tight cluster near shed, max 12 animals
# These tiles are RESERVED for animals only
PASTURE_SPOTS = [(4,4), (3,4), (4,3), (3,3), (4,2),
                 (3,2), (2,4), (2,3), (2,2), (4,1),
                 (3,1), (2,1)]
PASTURE_ZONE = set(PASTURE_SPOTS)

# Crop zone: top rows and left columns — NEVER build pastures here
# Tiles (0-1, 0-4) and (0-4, 0) are for crops

# Task priorities
P = {
    "FEED_CRIT": 2000, "WATER_CRIT": 1900, "PLACE": 1800,
    "BUILD_PASTURE": 1700,  # BUILD is high priority when animals are in shed
    "FEED": 1500, "CARE": 1400, "HARVEST": 1200,
    "COLLECT_FERT": 1100, "WATER": 1000, "FERTILIZE": 900,
    "PLANT": 800, "DIG": 600,
}

_STATE = {}

def _st(obs):
    p = obs["player"]
    s = obs["step"]
    if p not in _STATE or s == 0:
        _STATE[p] = {"fert_sold": False, "last_day": -1}
    st = _STATE[p]
    day = obs["day"]
    if day != st["last_day"]:
        st["last_day"] = day
        st["fert_sold"] = False
    return st

def _mv(a, b):
    ax, ay = a; bx, by = b
    if ax < bx: return "EAST"
    if ax > bx: return "WEST"
    if ay < by: return "SOUTH"
    if ay > by: return "NORTH"
    return "PASS"

def _dist(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _nearest_shed(pos):
    return min(SHED_ADJ, key=lambda s: _dist(pos, s))

# ─────────────────────────────────────────────────────────────────────────────
# MARKET
# ─────────────────────────────────────────────────────────────────────────────
def _market(obs, me, priv, st):
    ops = []
    day, hour = obs["day"], obs["hour"]
    money = me["money"]
    shed = priv["shed"]
    seeds = priv["seeds"]
    hires = me.get("hires_today", 0)
    invs = priv.get("inventories", [])
    prices = obs.get("market", {}).get("prices", {})
    tiles = me.get("tiles", [])

    if day == 0 and hour == 0:
        # OPENING: Buy wheat FIRST (exploit setup), animals, seeds
        # Market order cap = 10: 5 HIREs + BUY_PRODUCT + BUY_ANIMAL*2 + BUY_SEED*2
        for _ in range(min(5 - hires, 5)):
            ops.append(["HIRE"])
        ops.append(["BUY_PRODUCT", "WHEAT", 14])
        ops.append(["BUY_ANIMAL", "COW", 1])
        ops.append(["BUY_ANIMAL", "SHEEP", 4])
        ops.append(["BUY_SEED", "MELON", 5])

    elif day == 0 and hour == 1:
        # Sell wheat back (exploit) — but keep enough to feed animals for 2 days
        # With 5 animals needing 1 wheat/day: keep at least 10 wheat
        total_wheat = shed.get("WHEAT", 0) + sum(
            iv.get("WHEAT", 0) for iv in invs if isinstance(iv, dict))
        keep = 10  # 2 days worth of feed for 5 animals
        sell = max(0, total_wheat - keep)
        if sell > 0: ops.append(["SELL", "WHEAT", sell])
        # Seeds come AFTER we have fertilizer income (don't blow remaining $7 now)
        # Melon seeds will be bought on Day 2 when we have fert cash

    else:
        # DAILY OPERATIONS
        # Hire
        target_h = {0:5,1:1,2:2,3:3,4:4,5:5,6:5,7:6}.get(day, min(day+3, 8))
        if hour == 0:
            for _ in range(min(target_h - hires, 10)):
                ops.append(["HIRE"])

        # Sell fertilizer immediately (primary income from 5 animals)
        fert = shed.get("FERTILIZER", 0)
        if fert >= 5 and not st["fert_sold"] and hour <= 2:
            ops.append(["SELL", "FERTILIZER", min(fert, 10)])
            st["fert_sold"] = True

        # Feed animals — reactive wheat buying
        num_an = sum(1 for row in tiles for t in row
                     if isinstance(t, dict) and t.get("animal"))
        total_w = shed.get("WHEAT", 0) + sum(
            iv.get("WHEAT", 0) for iv in invs if isinstance(iv, dict))
        need = max(num_an + 2, 3)
        if total_w < need and money >= 35:
            ops.append(["BUY_PRODUCT", "WHEAT", min(need - total_w, 5)])
        # Buy seeds as money allows (after fertilizer income)
        # Wheat seeds to plant on empty tiles
        if seeds.get("WHEAT", 0) < 10 and money >= 100:
            buy_ws = min(10 - seeds.get("WHEAT", 0), max(0, (money - 50) // 5))
            if buy_ws > 0: ops.append(["BUY_SEED", "WHEAT", int(buy_ws)])
        # Melon seeds for high-value crop (expensive but worth it)
        if seeds.get("MELON", 0) < 8 and money >= 550 and day <= 10:
            buy_ms = min(8 - seeds.get("MELON", 0), 3)
            if buy_ms > 0: ops.append(["BUY_SEED", "MELON", buy_ms])

        if day >= 3 and hour == 0 and seeds.get("STRAWBERRY", 0) < 6 and money >= 250:
            ops.append(["BUY_SEED", "STRAWBERRY", 6])

        # Scale animals as money allows
        if hour == 0 and day >= 2:
            nc = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("animal") == "COW")
            ns = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("animal") == "SHEEP")
            tot = nc + ns + shed.get("COW", 0) + shed.get("SHEEP", 0)
            # Scale to 12+ animals like v057 — milk at $300 endgame is the key income
            if tot < 8 and money >= 400:
                ops.append(["BUY_ANIMAL", "COW", 1])
            elif tot < 12 and money >= 150:
                ops.append(["BUY_ANIMAL", "SHEEP", 1])

        # Sell products
        BASES = {"WOOL":200,"MILK":150,"EGG":100,"MELON":300,"STRAWBERRY":200}
        for prod in ["WOOL","MILK","EGG","MELON","STRAWBERRY"]:
            qty = shed.get(prod, 0)
            if qty <= 0: continue
            base = BASES[prod]
            price = prices.get(prod, base)
            if price >= base * 0.65 or day >= 25:
                ops.append(["SELL", prod, min(qty, 10)])
                if len(ops) >= 10: break

    return ops[:10]

# ─────────────────────────────────────────────────────────────────────────────
# TASK GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def _tasks(obs, me, priv):
    tasks = []
    day = obs["day"]
    tiles = me.get("tiles", [])
    shed = priv["shed"]
    seeds = priv["seeds"]
    invs = priv.get("inventories", [])

    occupied = set()
    for r, row in enumerate(tiles):
        for c, tile in enumerate(row or []):
            if not isinstance(tile, dict): continue
            kind = tile.get("kind")
            pos = (c, r)

            if kind in ("COOP", "PASTURE"):
                occupied.add(pos)
                an = tile.get("animal")
                if not an:
                    # Empty structure — place animal (high priority)
                    for animal in ["SHEEP", "COW"]:
                        has_it = (shed.get(animal, 0) > 0 or
                                  any(isinstance(iv, dict) and iv.get(animal, 0) > 0 for iv in invs))
                        if has_it:
                            tasks.append(("PLACE_" + animal, pos, P["PLACE"]))
                            break
                    continue
                consec = tile.get("consecutive_unfed", 0) or 0
                if not tile.get("fed_today"):
                    tasks.append(("FEED", pos, P["FEED_CRIT"] if consec > 0 else P["FEED"]))
                if not tile.get("cared_today"):
                    tasks.append(("CARE", pos, P["CARE"]))
                if (tile.get("yield_units") or 0) > 0:
                    tasks.append(("HARVEST", pos, P["HARVEST"]))
                if tile.get("fertilizer_available"):
                    tasks.append(("COLLECT_FERT", pos, P["COLLECT_FERT"]))

            elif kind == "PLANT":
                consec_uw = tile.get("consecutive_unwatered", 0) or 0
                if (tile.get("yield_units") or 0) > 0:
                    tasks.append(("HARVEST", pos, P["HARVEST"]))
                elif not tile.get("watered_today"):
                    prio = P["WATER_CRIT"] if consec_uw > 0 else P["WATER"]
                    tasks.append(("WATER", pos, prio))
                fert_until = tile.get("fertilized_until_day") or -1
                if fert_until < day and shed.get("FERTILIZER", 0) > 0:
                    tasks.append(("FERTILIZE", pos, P["FERTILIZE"]))

            elif kind == "WEED":
                tasks.append(("DIG", pos, P["DIG"]))

    # BUILD PASTURES: high priority if animals are in shed
    animals_in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
    # Also check inventories (animals might be carried)
    animals_in_inv = sum(
        iv.get("COW", 0) + iv.get("SHEEP", 0)
        for iv in invs if isinstance(iv, dict))
    if animals_in_shed > 0 or animals_in_inv > 0:
        for spot in PASTURE_SPOTS:
            c, r = spot
            if spot in occupied: continue
            if r >= len(tiles) or c >= len(tiles[r] or []): continue
            if tiles[r][c] is None:
                tasks.append(("BUILD_PASTURE", spot, P["BUILD_PASTURE"]))
                # Add multiple build tasks proportional to animals waiting
                needed = animals_in_shed + animals_in_inv
                built_so_far = len(occupied)
                if needed > 1 and built_so_far < needed:
                    for spot2 in PASTURE_SPOTS:
                        if spot2 == spot or spot2 in occupied: continue
                        c2, r2 = spot2
                        if r2 < len(tiles) and c2 < len(tiles[r2] or []) and tiles[r2][c2] is None:
                            tasks.append(("BUILD_PASTURE", spot2, P["BUILD_PASTURE"] - 1))
                            break
                break

    # PLANT seeds on empty NW tiles (CROP ZONE only — NOT in PASTURE_ZONE)
    for r in range(5):
        for c in range(5):
            pos = (c, r)
            if pos in SHED_ADJ or pos in occupied or pos in PASTURE_ZONE: continue
            row_data = tiles[r] if r < len(tiles) else []
            tile = row_data[c] if c < len(row_data) else None
            if tile is None:
                if seeds.get("WHEAT", 0) > 0:
                    tasks.append(("PLANT_WHEAT", pos, P["PLANT"]))
                elif seeds.get("MELON", 0) > 0 and day <= 12:
                    tasks.append(("PLANT_MELON", pos, P["PLANT"] - 10))
                elif seeds.get("STRAWBERRY", 0) > 0:
                    tasks.append(("PLANT_STRAW", pos, P["PLANT"] - 20))

    return tasks

# ─────────────────────────────────────────────────────────────────────────────
# TASK EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
FARM_ACTS = {
    "FEED": ["FEED"], "CARE": ["CARE"], "HARVEST": ["HARVEST"],
    "COLLECT_FERT": ["COLLECT_FERTILIZER"], "WATER": ["WATER"],
    "FERTILIZE": ["FERTILIZE"], "DIG": ["DIG"],
    "BUILD_PASTURE": ["BUILD_PASTURE"], "BUILD_COOP": ["BUILD_COOP"],
    "PLACE_COW": ["PLACE", "COW", 1], "PLACE_SHEEP": ["PLACE", "SHEEP", 1],
    "PLANT_WHEAT": ["PLANT", "WHEAT"], "PLANT_MELON": ["PLANT", "MELON"],
    "PLANT_STRAW": ["PLANT", "STRAWBERRY"],
}

def _exec(tt, tp, upos, inv, shed):
    inv = inv or {}
    # Need supply from shed?
    if tt == "FEED" and inv.get("WHEAT", 0) == 0:
        if shed.get("WHEAT", 0) > 0:
            if upos in SHED_ADJ: return ["PICKUP", "WHEAT", 5]
            return [_mv(upos, _nearest_shed(upos))]
        return ["PASS"]
    if tt == "FERTILIZE" and inv.get("FERTILIZER", 0) == 0:
        if shed.get("FERTILIZER", 0) > 0:
            if upos in SHED_ADJ: return ["PICKUP", "FERTILIZER", 5]
            return [_mv(upos, _nearest_shed(upos))]
        return ["PASS"]
    for an in ["COW", "SHEEP"]:
        if tt == f"PLACE_{an}" and inv.get(an, 0) == 0:
            if shed.get(an, 0) > 0:
                if upos in SHED_ADJ: return ["PICKUP", an, 1]
                return [_mv(upos, _nearest_shed(upos))]
            return ["PASS"]
    # Move or act
    if upos == tp:
        return FARM_ACTS.get(tt, ["PASS"])
    return [_mv(upos, tp)]

# ─────────────────────────────────────────────────────────────────────────────
# MAIN AGENT
# ─────────────────────────────────────────────────────────────────────────────
def agent(obs):
    try:
        player = obs["player"]
        me = obs["farms"][player]
        priv = obs["private"]
        shed = priv["shed"]
        invs = priv.get("inventories", [])

        st = _st(obs)
        market = _market(obs, me, priv, st)
        tasks = _tasks(obs, me, priv)

        farmer = tuple(me["farmer"])
        hands = [tuple(h) for h in me.get("hands", [])]
        units = [farmer] + hands
        n = len(units)
        acts = [["PASS"]] * n

        if tasks:
            # Cost matrix for Hungarian assignment
            cost = []
            for i, upos in enumerate(units):
                inv = invs[i] if i < len(invs) and isinstance(invs[i], dict) else {}
                row = []
                for (tt, tp, prio) in tasks:
                    d = _dist(upos, tp)
                    pen = 0
                    if tt == "FEED" and inv.get("WHEAT", 0) == 0: pen = 40
                    if tt == "FERTILIZE" and inv.get("FERTILIZER", 0) == 0: pen = 40
                    if tt.startswith("PLACE_"):
                        an = tt.split("_")[1]
                        if inv.get(an, 0) == 0: pen = 25
                    row.append(-prio + (d + pen) * 12)
                cost.append(row)

            ri, ci = linear_sum_assignment(cost)
            assigned = {r: tasks[c] for r, c in zip(ri, ci)}
            for i in range(n):
                if i not in assigned: continue
                tt, tp, _ = assigned[i]
                inv = invs[i] if i < len(invs) and isinstance(invs[i], dict) else {}
                acts[i] = _exec(tt, tp, units[i], inv, shed)

        # Drop inventory if idle at shed
        for i, upos in enumerate(units):
            if acts[i] == ["PASS"] and upos in SHED_ADJ:
                inv = invs[i] if i < len(invs) and isinstance(invs[i], dict) else {}
                if sum(inv.values()) > 0:
                    acts[i] = ["DROP"]

        return {"farmer": acts[0], "hands": acts[1:], "market": market}

    except Exception as e:
        import sys, traceback
        print(f"[v090 ERR step={obs.get('step','?')}]: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        farm = obs.get("farms", [{}])[obs.get("player", 0)]
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in farm.get("hands", [])], "market": []}
