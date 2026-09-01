import json
import glob
import os
import pandas as pd
import numpy as np

def analyze_replay(replay_path):
    try:
        with open(replay_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return None

    if "steps" not in data or len(data["steps"]) == 0:
        return None

    steps = data["steps"]
    final_step = steps[-1]
    
    # Identify players and rewards
    rewards = [s.get("reward", 0) for s in final_step]
    status = [s.get("status", "") for s in final_step]
    
    # We want to extract trajectory data
    # Each step[t] has [p0_state, p1_state]
    # Observation is in step[t][0]["observation"] (or step[t][p]["observation"])
    # Let's inspect step[0] structure
    ep_info = {
        "file": os.path.basename(replay_path),
        "steps_count": len(steps),
        "p0_reward": rewards[0] if len(rewards) > 0 else None,
        "p1_reward": rewards[1] if len(rewards) > 1 else None,
        "p0_status": status[0] if len(status) > 0 else None,
        "p1_status": status[1] if len(status) > 1 else None,
    }
    
    # Sample every 24 steps (end of each day)
    day_snapshots = []
    p0_hires = []
    p1_hires = []
    
    # Track actions across the match
    p0_market_sells = {}
    p1_market_sells = {}
    p0_plants = {}
    p1_plants = {}
    p0_animals = {}
    p1_animals = {}
    
    for t, step in enumerate(steps):
        # Extract actions
        for p_idx in [0, 1]:
            if p_idx < len(step):
                action = step[p_idx].get("action")
                if isinstance(action, dict):
                    # Market actions
                    m_orders = action.get("market", [])
                    for order in m_orders:
                        if isinstance(order, list) and len(order) > 0:
                            op = order[0]
                            if op == "SELL" and len(order) >= 3:
                                item, n = order[1], order[2]
                                target_dict = p0_market_sells if p_idx == 0 else p1_market_sells
                                target_dict[item] = target_dict.get(item, 0) + n
                            elif op == "BUY_ANIMAL" and len(order) >= 3:
                                animal, n = order[1], order[2]
                                target_dict = p0_animals if p_idx == 0 else p1_animals
                                target_dict[animal] = target_dict.get(animal, 0) + n
                    
                    # Farmer action
                    f_act = action.get("farmer", [])
                    if isinstance(f_act, list) and len(f_act) > 0:
                        if f_act[0] == "PLANT" and len(f_act) > 1:
                            crop = f_act[1]
                            target_dict = p0_plants if p_idx == 0 else p1_plants
                            target_dict[crop] = target_dict.get(crop, 0) + 1
                    
                    # Hands actions
                    h_acts = action.get("hands", [])
                    for ha in h_acts:
                        if isinstance(ha, list) and len(ha) > 0:
                            if ha[0] == "PLANT" and len(ha) > 1:
                                crop = ha[1]
                                target_dict = p0_plants if p_idx == 0 else p1_plants
                                target_dict[crop] = target_dict.get(crop, 0) + 1

    # Get end-of-game farm snapshot
    last_obs = None
    for step in reversed(steps):
        if "observation" in step[0] and step[0]["observation"]:
            last_obs = step[0]["observation"]
            break
            
    if last_obs and "farms" in last_obs:
        p0_farm = last_obs["farms"][0]
        p1_farm = last_obs["farms"][1]
        ep_info["p0_final_money"] = p0_farm.get("money")
        ep_info["p1_final_money"] = p1_farm.get("money")
        ep_info["p0_unlocked_quads"] = len(p0_farm.get("unlocked_quadrants", []))
        ep_info["p1_unlocked_quads"] = len(p1_farm.get("unlocked_quadrants", []))
        ep_info["p0_hands_count"] = len(p0_farm.get("hands", []))
        ep_info["p1_hands_count"] = len(p1_farm.get("hands", []))
    
    ep_info["p0_plants"] = p0_plants
    ep_info["p1_plants"] = p1_plants
    ep_info["p0_animals"] = p0_animals
    ep_info["p1_animals"] = p1_animals
    ep_info["p0_sells"] = p0_market_sells
    ep_info["p1_sells"] = p1_market_sells
    
    return ep_info

def main():
    files = sorted(glob.glob("kaggle_episodes/*.json"))
    print(f"Found {len(files)} replay files to analyze.")
    
    results = []
    for f in files:
        if "agent-0-logs" in f:
            continue
        info = analyze_replay(f)
        if info:
            results.append(info)
            
    print(f"\nSuccessfully parsed {len(results)} matches.")
    
    rows = []
    for r in results:
        p0_m = r.get("p0_final_money", r.get("p0_reward", 0))
        p1_m = r.get("p1_final_money", r.get("p1_reward", 0))
        p0_q = r.get("p0_unlocked_quads", 0)
        p1_q = r.get("p1_unlocked_quads", 0)
        p0_h = r.get("p0_hands_count", 0)
        p1_h = r.get("p1_hands_count", 0)
        
        winner = "P0" if p0_m > p1_m else ("P1" if p1_m > p0_m else "TIE")
        max_score = max(p0_m, p1_m)
        min_score = min(p0_m, p1_m)
        
        rows.append({
            "File": r["file"],
            "P0_Money": p0_m,
            "P1_Money": p1_m,
            "Winner": winner,
            "Top_Score": max_score,
            "P0_Quads": p0_q,
            "P1_Quads": p1_q,
            "P0_Hands": p0_h,
            "P1_Hands": p1_h,
            "P0_Plants": str(r["p0_plants"]),
            "P1_Plants": str(r["p1_plants"]),
            "P0_Animals": str(r["p0_animals"]),
            "P1_Animals": str(r["p1_animals"]),
            "P0_Sells": str(r["p0_sells"]),
            "P1_Sells": str(r["p1_sells"]),
        })
        
    df = pd.DataFrame(rows)
    print("\n=== MATCH SUMMARY TABLE (SORTED BY TOP SCORE) ===")
    df_sorted = df.sort_values(by="Top_Score", ascending=False)
    print(df_sorted[["File", "Winner", "Top_Score", "P0_Money", "P1_Money", "P0_Quads", "P1_Quads", "P0_Hands", "P1_Hands"]].head(25).to_string(index=False))
    
    print("\n=== TOP 5 HIGHEST SCORING GAMES DETAILED BREAKDOWN ===")
    for idx, row in df_sorted.head(5).iterrows():
        print(f"\n--- {row['File']} (Top Score: ${row['Top_Score']:,}, Winner: {row['Winner']}) ---")
        print(f"  P0 ($ {row['P0_Money']:,}, Quads: {row['P0_Quads']}, Hands: {row['P0_Hands']}):")
        print(f"    Plants:  {row['P0_Plants']}")
        print(f"    Animals: {row['P0_Animals']}")
        print(f"    Sells:   {row['P0_Sells']}")
        print(f"  P1 ($ {row['P1_Money']:,}, Quads: {row['P1_Quads']}, Hands: {row['P1_Hands']}):")
        print(f"    Plants:  {row['P1_Plants']}")
        print(f"    Animals: {row['P1_Animals']}")
        print(f"    Sells:   {row['P1_Sells']}")

if __name__ == "__main__":
    main()
