"""
Phase 1: Reconstruct the Day 0->10 Economic Engine (Episode 103388734)
=====================================================================
Builds an hourly cash-flow ledger for Days 0 to 10:
HOUR | BANK | REVENUE | EXPENSE | WOOL_SOLD | FERT_SOLD | COWS_BOUGHT | PASTURES_BOUGHT | STRAWBERRY_SEEDS | WHEAT | WORKERS | LAND | MARKET_SALES
"""

import json
import os
import pandas as pd

def build_hourly_ledger(replay_path="kaggle_episodes/episode-103388734-replay.json", target_player=1):
    with open(replay_path, "r") as f:
        data = json.load(f)
    steps = data["steps"]
    
    records = []
    
    prev_money = steps[0][target_player]["observation"]["farms"][target_player]["money"]
    
    for step_idx in range(min(11 * 24, len(steps))):
        day = step_idx // 24
        hour = step_idx % 24
        
        step = steps[step_idx]
        obs = step[target_player]["observation"]
        farm = obs["farms"][target_player]
        cur_money = farm["money"]
        
        delta_money = cur_money - prev_money
        
        # Parse actions
        act = step[target_player].get("action", {})
        if not isinstance(act, dict):
            act = {}
            
        m_orders = act.get("market", [])
        
        wool_sold = 0
        fert_sold = 0
        straw_sold = 0
        milk_sold = 0
        melon_sold = 0
        wheat_sold = 0
        
        cows_bought = 0
        sheep_bought = 0
        straw_seeds_bought = 0
        wheat_seeds_bought = 0
        melon_seeds_bought = 0
        wheat_feed_bought = 0
        hires = 0
        land_bought = 0
        
        for o in m_orders:
            if not isinstance(o, list) or len(o) == 0: continue
            op = o[0]
            if op == "SELL" and len(o) >= 3:
                prod = o[1]
                qty = o[2]
                if prod == "WOOL": wool_sold += qty
                elif prod == "FERTILIZER": fert_sold += qty
                elif prod == "STRAWBERRY": straw_sold += qty
                elif prod == "MILK": milk_sold += qty
                elif prod == "MELON": melon_sold += qty
                elif prod == "WHEAT": wheat_sold += qty
            elif op == "BUY_ANIMAL" and len(o) >= 3:
                an = o[1]
                qty = o[2]
                if an == "COW": cows_bought += qty
                elif an == "SHEEP": sheep_bought += qty
            elif op == "BUY_SEED" and len(o) >= 3:
                sd = o[1]
                qty = o[2]
                if sd == "STRAWBERRY": straw_seeds_bought += qty
                elif sd == "WHEAT": wheat_seeds_bought += qty
                elif sd == "MELON": melon_seeds_bought += qty
            elif op == "BUY_PRODUCT" and len(o) >= 3:
                qty = o[2]
                if o[1] == "WHEAT": wheat_feed_bought += qty
            elif op == "HIRE":
                hires += 1
            elif op == "BUY_LAND":
                land_bought += 1
                
        all_u = [act.get("farmer", [])] + act.get("hands", [])
        pastures_built = 0
        coops_built = 0
        plants_planted = {}
        digs = 0
        
        for u in all_u:
            if not isinstance(u, list) or len(u) == 0: continue
            u_op = u[0]
            if u_op == "BUILD_PASTURE": pastures_built += 1
            elif u_op == "BUILD_COOP": coops_built += 1
            elif u_op == "PLANT" and len(u) > 1:
                crop = u[1]
                plants_planted[crop] = plants_planted.get(crop, 0) + 1
            elif u_op == "DIG": digs += 1
            
        # Count farm assets
        cows_on_farm = 0
        sheep_on_farm = 0
        straw_on_farm = 0
        wheat_on_farm = 0
        melons_on_farm = 0
        for row in farm["tiles"]:
            for cell in row:
                if isinstance(cell, dict):
                    k = cell.get("kind")
                    if k in ["PASTURE", "COOP"]:
                        an = cell.get("animal")
                        if an == "COW": cows_on_farm += 1
                        elif an == "SHEEP": sheep_on_farm += 1
                    elif k == "PLANT":
                        cr = cell.get("crop")
                        if cr == "STRAWBERRY": straw_on_farm += 1
                        elif cr == "WHEAT": wheat_on_farm += 1
                        elif cr == "MELON": melons_on_farm += 1
                        
        num_hands = len(farm["hands"])
        num_quads = len(farm["unlocked_quadrants"])
        
        revenue = max(0, delta_money)
        expense = max(0, -delta_money)
        
        records.append({
            "STEP": step_idx,
            "DAY": day,
            "HOUR": hour,
            "BANK": cur_money,
            "DELTA": delta_money,
            "REVENUE": revenue,
            "EXPENSE": expense,
            "WOOL_SOLD": wool_sold,
            "FERT_SOLD": fert_sold,
            "MILK_SOLD": milk_sold,
            "STRAW_SOLD": straw_sold,
            "MELON_SOLD": melon_sold,
            "COWS_BOUGHT": cows_bought,
            "SHEEP_BOUGHT": sheep_bought,
            "PASTURES_BUILT": pastures_built,
            "STRAW_SEEDS_BOUGHT": straw_seeds_bought,
            "STRAW_PLANTED": plants_planted.get("STRAWBERRY", 0),
            "WHEAT_SEEDS_BOUGHT": wheat_seeds_bought,
            "WHEAT_FEED_BOUGHT": wheat_feed_bought,
            "WHEAT_PLANTED": plants_planted.get("WHEAT", 0),
            "WORKERS": 1 + num_hands,
            "HIRES": hires,
            "LAND_BOUGHT": land_bought,
            "QUADS": num_quads,
            "COWS_TOTAL": cows_on_farm,
            "SHEEP_TOTAL": sheep_on_farm,
            "STRAW_TOTAL": straw_on_farm,
            "WHEAT_TOTAL": wheat_on_farm,
            "MELONS_TOTAL": melons_on_farm,
        })
        
        prev_money = cur_money
        
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = build_hourly_ledger()
    print("=" * 130)
    print("HOURLY CASH-FLOW LEDGER FOR TOP REPLAY (Episode 103388734) - DAYS 0 TO 10")
    print("=" * 130)
    
    # Print daily aggregated summary
    daily_summary = df.groupby("DAY").agg({
        "BANK": "last",
        "REVENUE": "sum",
        "EXPENSE": "sum",
        "WOOL_SOLD": "sum",
        "FERT_SOLD": "sum",
        "MILK_SOLD": "sum",
        "COWS_BOUGHT": "sum",
        "SHEEP_BOUGHT": "sum",
        "PASTURES_BUILT": "sum",
        "STRAW_SEEDS_BOUGHT": "sum",
        "STRAW_PLANTED": "sum",
        "WHEAT_PLANTED": "sum",
        "WORKERS": "last",
        "QUADS": "last",
        "COWS_TOTAL": "last",
        "SHEEP_TOTAL": "last",
        "STRAW_TOTAL": "last",
    }).reset_index()
    
    print("\n--- DAILY AGGREGATED SUMMARY (DAYS 0-10) ---")
    print(daily_summary.to_string(index=False))
    
    # Print key transaction hours
    print("\n--- KEY TRANSACTIONS (EXPENSE > 0 OR REVENUE > 0) ---")
    tx_df = df[(df["EXPENSE"] > 0) | (df["REVENUE"] > 0)][[
        "DAY", "HOUR", "BANK", "DELTA", "WOOL_SOLD", "FERT_SOLD", "MILK_SOLD", 
        "COWS_BOUGHT", "SHEEP_BOUGHT", "PASTURES_BUILT", "STRAW_SEEDS_BOUGHT", 
        "WORKERS", "LAND_BOUGHT", "QUADS", "COWS_TOTAL", "STRAW_TOTAL"
    ]]
    print(tx_df.head(45).to_string(index=False))
