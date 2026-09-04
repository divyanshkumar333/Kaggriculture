import json
import os

def trace_operations():
    with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    p = 1
    
    print("=== OPERATION DETAILS DAYS 20-29 (EPISODE 103388734) ===")
    for day in range(20, 30):
        print(f"\n--- DAY {day} ---")
        day_steps = steps[day*24 : (day+1)*24]
        
        # Check start of day
        obs0 = day_steps[0][0]["observation"]
        f0 = obs0["farms"][p]
        hands_cnt = len(f0["hands"])
        money_d = f0["money"]
        
        digs = []
        plants = []
        ferts = []
        harvests = []
        sells = []
        buys = []
        
        for h, step in enumerate(day_steps):
            act = step[p].get("action")
            if not isinstance(act, dict): continue
            
            m_orders = act.get("market", [])
            for o in m_orders:
                if isinstance(o, list) and len(o) > 0:
                    if o[0] == "SELL":
                        sells.append(f"H{h}:{o[1]}x{o[2]}")
                    elif o[0] in ["BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"]:
                        buys.append(f"H{h}:{o[0]}_{o[1]}x{o[2]}")
                    elif o[0] in ["BUY_LAND", "HIRE"]:
                        buys.append(f"H{h}:{o[0]}")
                        
            all_units = [act.get("farmer", [])] + act.get("hands", [])
            for u_idx, u in enumerate(all_units):
                if isinstance(u, list) and len(u) > 0:
                    u_op = u[0]
                    if u_op == "DIG":
                        digs.append(f"H{h}:U{u_idx}")
                    elif u_op == "PLANT":
                        plants.append(f"H{h}:U{u_idx}_{u[1]}")
                    elif u_op == "FERTILIZE":
                        ferts.append(f"H{h}:U{u_idx}")
                    elif u_op == "HARVEST":
                        harvests.append(f"H{h}:U{u_idx}")
                        
        print(f"Money: ${money_d:,.0f} | Hands: {hands_cnt}")
        print(f"Buys: {', '.join(buys[:8])}")
        print(f"Sells: {', '.join(sells[:8])}")
        print(f"Plants ({len(plants)}): {', '.join(plants[:10])}")
        print(f"Digs ({len(digs)}): {', '.join(digs[:10])}")
        print(f"Fertilizes: {len(ferts)} | Harvests: {len(harvests)}")

if __name__ == "__main__":
    trace_operations()
