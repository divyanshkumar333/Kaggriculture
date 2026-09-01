import json
import os
import pandas as pd

def deep_trace(replay_path, target_player=1):
    with open(replay_path, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    print(f"\n=======================================================")
    print(f"DEEP TRACE: {os.path.basename(replay_path)} | PLAYER {target_player}")
    print(f"=======================================================")
    
    # Track day by day
    # 24 steps per day
    num_days = len(steps) // 24
    
    daily_stats = []
    
    for day in range(num_days):
        day_steps = steps[day*24 : (day+1)*24]
        
        # Start of day state
        start_step = day_steps[0]
        end_step = day_steps[-1]
        
        obs_start = start_step[0]["observation"]
        obs_end = end_step[0]["observation"]
        
        p_farm_start = obs_start["farms"][target_player]
        p_farm_end = obs_end["farms"][target_player]
        
        money_start = p_farm_start["money"]
        money_end = p_farm_end["money"]
        quads = len(p_farm_end["unlocked_quadrants"])
        hands = len(p_farm_end["hands"])
        
        # Scan actions during this day
        sells = {}
        buys = {}
        plants = {}
        animals_placed = {}
        structures_built = {}
        cared_count = 0
        fed_count = 0
        watered_count = 0
        harvested_count = 0
        fertilizer_collected = 0
        
        # Count tile contents at end of day
        tiles = p_farm_end["tiles"]
        tile_counts = {"EMPTY": 0, "LOCKED": 0, "WEED": 0, "PLANTS": {}, "ANIMALS": {}}
        for r in range(10):
            for c in range(10):
                tile = tiles[r][c]
                if tile is None:
                    tile_counts["EMPTY"] += 1
                elif tile == "LOCKED":
                    tile_counts["LOCKED"] += 1
                elif isinstance(tile, dict):
                    kind = tile.get("kind")
                    if kind == "WEED":
                        tile_counts["WEED"] += 1
                    elif kind == "PLANT":
                        crop = tile.get("crop", "UNKNOWN")
                        tile_counts["PLANTS"][crop] = tile_counts["PLANTS"].get(crop, 0) + 1
                    elif kind in ["COOP", "PASTURE"]:
                        an = tile.get("animal")
                        if an:
                            tile_counts["ANIMALS"][an] = tile_counts["ANIMALS"].get(an, 0) + 1
                        else:
                            tile_counts["ANIMALS"][f"EMPTY_{kind}"] = tile_counts["ANIMALS"].get(f"EMPTY_{kind}", 0) + 1

        for step in day_steps:
            act = step[target_player].get("action")
            if not isinstance(act, dict):
                continue
                
            m_orders = act.get("market", [])
            for o in m_orders:
                if isinstance(o, list) and len(o) > 0:
                    op = o[0]
                    if op == "SELL" and len(o) >= 3:
                        sells[o[1]] = sells.get(o[1], 0) + o[2]
                    elif op in ["BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"] and len(o) >= 3:
                        buys[f"{op}_{o[1]}"] = buys.get(f"{op}_{o[1]}", 0) + o[2]
                    elif op in ["BUY_LAND", "HIRE"]:
                        buys[op] = buys.get(op, 0) + 1
                        
            all_unit_acts = [act.get("farmer", [])] + act.get("hands", [])
            for u in all_unit_acts:
                if isinstance(u, list) and len(u) > 0:
                    u_op = u[0]
                    if u_op == "PLANT" and len(u) > 1:
                        plants[u[1]] = plants.get(u[1], 0) + 1
                    elif u_op == "CARE":
                        cared_count += 1
                    elif u_op == "FEED":
                        fed_count += 1
                    elif u_op == "WATER":
                        watered_count += 1
                    elif u_op == "HARVEST":
                        harvested_count += 1
                    elif u_op == "COLLECT_FERTILIZER":
                        fertilizer_collected += 1
                    elif u_op in ["BUILD_PASTURE", "BUILD_COOP"]:
                        structures_built[u_op] = structures_built.get(u_op, 0) + 1
                    elif u_op == "PLACE" and len(u) > 1:
                        animals_placed[u[1]] = animals_placed.get(u[1], 0) + 1
                        
        daily_stats.append({
            "Day": day,
            "StartMoney": money_start,
            "EndMoney": money_end,
            "Quads": quads,
            "Hands": hands,
            "Buys": buys,
            "Sells": sells,
            "Plants": plants,
            "Tile_Plants": tile_counts["PLANTS"],
            "Tile_Animals": tile_counts["ANIMALS"],
            "Cared": cared_count,
            "Fed": fed_count,
            "Watered": watered_count,
            "Harvested": harvested_count,
            "FertilizerCollected": fertilizer_collected,
        })
        
    df = pd.DataFrame(daily_stats)
    for idx, row in df.iterrows():
        print(f"Day {row['Day']:2d} | Money: ${row['StartMoney']:,.0f} -> ${row['EndMoney']:,.0f} | Quads: {row['Quads']} | Hands: {row['Hands']} | Plants: {row['Tile_Plants']} | Animals: {row['Tile_Animals']}")
        if row['Buys']:
            print(f"       BUYS:  {row['Buys']}")
        if row['Sells']:
            print(f"       SELLS: {row['Sells']}")
        if row['Plants']:
            print(f"       PLANTED TODAY: {row['Plants']}")
        if row['Cared'] or row['Fed'] or row['FertilizerCollected']:
            print(f"       WORK: Fed={row['Fed']}, Cared={row['Cared']}, FertColl={row['FertilizerCollected']}, Wat={row['Watered']}, Harv={row['Harvested']}")

if __name__ == "__main__":
    deep_trace("kaggle_episodes/episode-103388734-replay.json", target_player=1)
    deep_trace("kaggle_episodes/episode-103979994-replay.json", target_player=0)
