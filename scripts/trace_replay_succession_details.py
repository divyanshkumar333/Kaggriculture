import json
import os
import glob
import pandas as pd

def analyze_replay_succession(replay_path, target_player=None):
    with open(replay_path, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    
    # Auto-detect target player if None (player with highest reward)
    if target_player is None:
        final_step = steps[-1]
        r0 = final_step[0].get("reward", 0) or 0
        r1 = final_step[1].get("reward", 0) or 0
        target_player = 0 if r0 >= r1 else 1
        
    final_reward = steps[-1][target_player].get("reward", 0)
    print(f"\n=======================================================")
    print(f"EPISODE: {os.path.basename(replay_path)} | PLAYER {target_player} | FINAL REWARD: ${final_reward:,.0f}")
    print(f"=======================================================")
    
    num_days = len(steps) // 24
    
    daily_records = []
    
    prev_strawberry_positions = set()
    prev_tile_states = {}
    
    for day in range(num_days):
        day_steps = steps[day*24 : (day+1)*24]
        
        obs_start = day_steps[0][0]["observation"]
        obs_end = day_steps[-1][0]["observation"]
        
        farm_start = obs_start["farms"][target_player]
        farm_end = obs_end["farms"][target_player]
        
        start_money = farm_start["money"]
        end_money = farm_end["money"]
        
        # Track events during the day
        strawberry_planted = 0
        wheat_planted = 0
        wheat_harvested = 0
        strawberry_harvested = 0
        wheat_sold = 0
        wheat_sold_revenue = 0
        fertilizer_used = 0
        dig_cleared = 0
        decay_events = 0
        
        # Action parsing
        for step_idx, step in enumerate(day_steps):
            hour = step_idx
            act = step[target_player].get("action")
            if not isinstance(act, dict):
                continue
                
            m_orders = act.get("market", [])
            for o in m_orders:
                if isinstance(o, list) and len(o) > 0:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT":
                        wheat_sold += o[2]
                        # Estimate price from market observation if available
                        m_prices = step[0]["observation"].get("market", {}).get("prices", {})
                        wheat_sold_revenue += o[2] * m_prices.get("WHEAT", 60)
                        
            all_unit_acts = [act.get("farmer", [])] + act.get("hands", [])
            for u in all_unit_acts:
                if isinstance(u, list) and len(u) > 0:
                    u_op = u[0]
                    if u_op == "PLANT" and len(u) > 1:
                        if u[1] == "STRAWBERRY":
                            strawberry_planted += 1
                        elif u[1] == "WHEAT":
                            wheat_planted += 1
                    elif u_op == "HARVEST":
                        # We can inspect what was on that tile or observe inventory changes
                        pass
                    elif u_op == "DIG":
                        dig_cleared += 1
                    elif u_op == "FERTILIZE":
                        fertilizer_used += 1

        # Count tile contents at end of day
        tiles = farm_end["tiles"]
        strawberry_count = 0
        wheat_count = 0
        empty_count = 0
        weed_count = 0
        current_strawberry_positions = set()
        
        for r in range(10):
            for c in range(10):
                tile = tiles[r][c]
                if tile is None:
                    empty_count += 1
                elif isinstance(tile, dict):
                    kind = tile.get("kind")
                    if kind == "WEED":
                        weed_count += 1
                    elif kind == "PLANT":
                        crop = tile.get("crop")
                        if crop == "STRAWBERRY":
                            strawberry_count += 1
                            current_strawberry_positions.add((c, r))
                        elif crop == "WHEAT":
                            wheat_count += 1
                            if tile.get("yield_units", 0) > 0 and (day - tile.get("planted_day", day)) >= 2:
                                # Count ripe wheat
                                pass

        # Detect strawberries that vanished/decayed since previous day
        freed_tiles = len(prev_strawberry_positions - current_strawberry_positions)
        prev_strawberry_positions = current_strawberry_positions
        
        daily_records.append({
            "DAY": day,
            "STRAWBERRIES": strawberry_count,
            "FREED_TILES": freed_tiles,
            "WHEAT_PLANTED": wheat_planted,
            "WHEAT_ON_TILES": wheat_count,
            "WHEAT_SOLD": wheat_sold,
            "DIG_CLEARED": dig_cleared,
            "FERTILIZE_USED": fertilizer_used,
            "EMPTY_TILES": empty_count,
            "WEED_TILES": weed_count,
            "BANK_START": start_money,
            "BANK_END": end_money,
            "BANK_DELTA": end_money - start_money
        })
        
    df = pd.DataFrame(daily_records)
    print("\n--- DAYS 15-30 SUCCESSION MATRIX ---")
    sub_df = df[df["DAY"] >= 15][["DAY", "STRAWBERRIES", "FREED_TILES", "WHEAT_PLANTED", "WHEAT_ON_TILES", "WHEAT_SOLD", "DIG_CLEARED", "EMPTY_TILES", "BANK_END", "BANK_DELTA"]]
    print(sub_df.to_string(index=False))
    return df

if __name__ == "__main__":
    print("ANALYZING RECORD REPLAY 103388734:")
    df_top = analyze_replay_succession("kaggle_episodes/episode-103388734-replay.json", target_player=1)
    
    # Check other replays in kaggle_episodes
    replays = glob.glob("kaggle_episodes/episode-*-replay.json")
    print(f"\nChecking other {len(replays)} replays for late-game succession patterns...")
    
    summary_list = []
    for r in replays:
        if "103388734" in r: continue
        with open(r, "r") as f:
            data = json.load(f)
        steps = data["steps"]
        r0 = steps[-1][0].get("reward", 0) or 0
        r1 = steps[-1][1].get("reward", 0) or 0
        top_p = 0 if r0 >= r1 else 1
        top_r = max(r0, r1)
        
        # Check wheat planted on days 20-28 and strawberries on day 15
        p_farm_d15 = steps[15*24][0]["observation"]["farms"][top_p]
        p_farm_d25 = steps[25*24][0]["observation"]["farms"][top_p]
        
        straw_d15 = 0
        for row in p_farm_d15["tiles"]:
            for cell in row:
                if isinstance(cell, dict) and cell.get("kind") == "PLANT" and cell.get("crop") == "STRAWBERRY":
                    straw_d15 += 1
                    
        wheat_planted_d20_28 = 0
        for d in range(20, min(len(steps)//24, 29)):
            for st in steps[d*24 : (d+1)*24]:
                act = st[top_p].get("action")
                if isinstance(act, dict):
                    all_acts = [act.get("farmer", [])] + act.get("hands", [])
                    for a in all_acts:
                        if isinstance(a, list) and len(a) > 1 and a[0] == "PLANT" and a[1] == "WHEAT":
                            wheat_planted_d20_28 += 1
                            
        summary_list.append({
            "replay": os.path.basename(r),
            "player": top_p,
            "reward": top_r,
            "strawberries_d15": straw_d15,
            "late_wheat_planted": wheat_planted_d20_28
        })
        
    df_sum = pd.DataFrame(summary_list).sort_values("reward", ascending=False)
    print("\n--- TOP REPLAYS LATE WHEAT / STRAWBERRY PATTERN ---")
    print(df_sum.head(15).to_string(index=False))
