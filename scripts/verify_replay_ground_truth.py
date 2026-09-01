import json
import os
import pandas as pd
import numpy as np

def verify_replay(replay_path):
    with open(replay_path, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    print(f"Loaded {replay_path}, total steps: {len(steps)}")
    
    # We want to extract Player 1 (the 162k agent) and Player 0 (the opponent)
    # Check config
    env_config = data.get("configuration", {})
    print(f"Env Configuration: {env_config}")
    
    # Step 0 observation
    obs0 = steps[0][0]["observation"]
    print(f"Initial bank P0: {obs0['farms'][0]['money']}, P1: {obs0['farms'][1]['money']}")
    
    # Turn by turn trace for Day 0 (turns 0..23)
    print("\n=======================================================")
    print("DAY 0 DETAILED STEP-BY-STEP TRACE (PLAYER 1)")
    print("=======================================================")
    
    for t in range(24):
        s = steps[t]
        act_p1 = s[1].get("action")
        obs_t = s[0]["observation"] if "observation" in s[0] else None
        p1_farm = obs_t["farms"][1] if obs_t and "farms" in obs_t else None
        
        m_orders = act_p1.get("market", []) if isinstance(act_p1, dict) else []
        f_act = act_p1.get("farmer", []) if isinstance(act_p1, dict) else []
        h_acts = act_p1.get("hands", []) if isinstance(act_p1, dict) else []
        
        if m_orders or f_act or h_acts:
            print(f"Turn {t:2d} (Hour {t:2d}):")
            if p1_farm:
                print(f"   Bank: ${p1_farm['money']:.0f} | Farmer at {p1_farm['farmer']} | Hands at {p1_farm['hands']}")
            if m_orders:
                print(f"   Market Orders: {m_orders}")
            if f_act:
                print(f"   Farmer: {f_act}")
            if h_acts:
                print(f"   Hands:  {h_acts}")
                
    # Day-by-Day summary table
    print("\n=======================================================")
    print("DAY-BY-DAY ECONOMIC & ACTION AUDIT (P1)")
    print("=======================================================")
    
    daily_records = []
    
    for day in range(30):
        day_steps = steps[day*24 : (day+1)*24]
        
        # Start and end observations
        start_obs = day_steps[0][0].get("observation")
        end_obs = day_steps[-1][0].get("observation")
        
        p1_start = start_obs["farms"][1] if start_obs else {}
        p1_end = end_obs["farms"][1] if end_obs else {}
        
        money_start = p1_start.get("money", 0)
        money_end = p1_end.get("money", 0)
        quads = len(p1_end.get("unlocked_quadrants", []))
        hands = len(p1_end.get("hands", []))
        
        # Aggregates for the day
        sells = {}
        buys = {}
        farmer_actions = {}
        hand_actions = {}
        
        # Action breakdown
        cared = 0
        fed = 0
        watered = 0
        harvested = 0
        fert_collected = 0
        planted = {}
        built = {}
        placed = {}
        
        for s in day_steps:
            act = s[1].get("action", {})
            if not isinstance(act, dict):
                continue
                
            for m in act.get("market", []):
                if not isinstance(m, list) or len(m) == 0: continue
                op = m[0]
                if op == "SELL" and len(m) >= 3:
                    sells[m[1]] = sells.get(m[1], 0) + m[2]
                elif op in ["BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"] and len(m) >= 3:
                    key = f"{op}_{m[1]}"
                    buys[key] = buys.get(key, 0) + m[2]
                elif op in ["BUY_LAND", "HIRE"]:
                    buys[op] = buys.get(op, 0) + 1
                    
            all_u = [act.get("farmer", [])] + act.get("hands", [])
            for u in all_u:
                if not isinstance(u, list) or len(u) == 0: continue
                u_op = u[0]
                if u_op == "CARE": cared += 1
                elif u_op == "FEED": fed += 1
                elif u_op == "WATER": watered += 1
                elif u_op == "HARVEST": harvested += 1
                elif u_op == "COLLECT_FERTILIZER": fert_collected += 1
                elif u_op == "PLANT" and len(u) > 1:
                    planted[u[1]] = planted.get(u[1], 0) + 1
                elif u_op in ["BUILD_PASTURE", "BUILD_COOP"]:
                    built[u_op] = built.get(u_op, 0) + 1
                elif u_op == "PLACE" and len(u) > 1:
                    placed[u[1]] = placed.get(u[1], 0) + 1
                    
        # Tiles audit
        tiles = p1_end.get("tiles", [])
        plants_on_board = {}
        animals_on_board = {}
        for r in range(len(tiles)):
            for c in range(len(tiles[r])):
                t = tiles[r][c]
                if isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        cr = t.get("crop", "UNK")
                        plants_on_board[cr] = plants_on_board.get(cr, 0) + 1
                    elif t.get("kind") in ["PASTURE", "COOP"]:
                        an = t.get("animal")
                        if an:
                            animals_on_board[an] = animals_on_board.get(an, 0) + 1
                        else:
                            animals_on_board[f"EMPTY_{t.get('kind')}"] = animals_on_board.get(f"EMPTY_{t.get('kind')}", 0) + 1
                            
        # Town shops unlocked
        town_shops = start_obs.get("town", {}).get("unlocked_shops", []) if start_obs else []
        
        # Market prices
        mkt_prices = start_obs.get("market", {}).get("prices", {}) if start_obs else {}
        
        daily_records.append({
            "Day": day,
            "StartMoney": money_start,
            "EndMoney": money_end,
            "DeltaMoney": money_end - money_start,
            "Quads": quads,
            "Hands": hands,
            "Plants": plants_on_board,
            "Animals": animals_on_board,
            "Buys": buys,
            "Sells": sells,
            "Planted": planted,
            "Built": built,
            "Placed": placed,
            "Cared": cared,
            "Fed": fed,
            "Watered": watered,
            "Harvested": harvested,
            "FertColl": fert_collected,
            "ShopsCount": len(town_shops),
            "Prices": mkt_prices
        })
        
    df = pd.DataFrame(daily_records)
    return df, data

if __name__ == "__main__":
    df, data = verify_replay("kaggle_episodes/episode-103388734-replay.json")
    for idx, r in df.iterrows():
        print(f"Day {r['Day']:2d} | Cash: ${r['StartMoney']:>8,.0f} -> ${r['EndMoney']:>8,.0f} (d: ${r['DeltaMoney']:>+7,.0f}) | Quads: {r['Quads']} | Hands: {r['Hands']:2d} | Animals: {r['Animals']} | Crops: {r['Plants']}")
        if r['Buys']: print(f"       BUYS:   {r['Buys']}")
        if r['Sells']: print(f"       SELLS:  {r['Sells']}")
        if r['Planted'] or r['Built'] or r['Placed']: print(f"       SPATIAL: Built={r['Built']}, Placed={r['Placed']}, Planted={r['Planted']}")
        print(f"       ACTIONS: Fed={r['Fed']}, Cared={r['Cared']}, FertColl={r['FertColl']}, Wat={r['Watered']}, Harv={r['Harvested']}")
