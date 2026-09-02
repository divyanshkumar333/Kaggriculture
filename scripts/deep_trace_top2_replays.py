"""
Deep Replay Tracer for #1 ($162.8k) and #2 ($114.8k) Replays
-------------------------------------------------------------
Traces every hour of every day to find:
- Market sales: what products, what batch sizes, what hours, what sale prices
- Land purchases: what exact day/hour
- Animal purchases: what exact day/hour
- Labor hiring: exact worker counts by hour
- Fertilizer usage: was fertilizer used on crops, or sold to market?
"""

import json

def trace_top_replay(ep_id, p_idx):
    fpath = f"kaggle_episodes/episode-{ep_id}-replay.json"
    with open(fpath, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    print("="*110)
    print(f"DEEP TRACE: Episode {ep_id} (Player {p_idx}) -> Final Score: {steps[-1][p_idx]['reward']}")
    print("="*110)
    
    print(f"{'DAY':<4} | {'HOUR':<4} | {'BANK':<8} | {'HANDS':<5} | {'QUADS':<5} | {'COWS':<4} | {'SHEEP':<5} | {'CROPS SUMMARY':<28} | {'MARKET ORDERS':<35}")
    print("-"*110)
    
    for d in range(30):
        # We sample hour 0, hour 1, and hour 23
        for h in [0, 1, 12, 23]:
            step_idx = d * 24 + h
            if step_idx >= len(steps): break
            step_data = steps[step_idx]
            obs = step_data[p_idx]["observation"]
            act = step_data[p_idx].get("action", {})
            farm = obs["farms"][p_idx]
            priv = obs.get("private", {})
            
            bank = farm["money"]
            hands = len(farm.get("hands", []))
            quads = len(farm.get("unlocked_quadrants", []))
            
            cows, sheep = 0, 0
            crop_counts = {}
            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict):
                        k = t.get("kind")
                        if k in ["PASTURE", "COOP"]:
                            an = t.get("animal")
                            if an == "COW": cows += 1
                            elif an == "SHEEP": sheep += 1
                        elif k == "PLANT":
                            cr = t.get("crop")
                            crop_counts[cr] = crop_counts.get(cr, 0) + 1
                            
            crops_str = ", ".join([f"{k}:{v}" for k, v in crop_counts.items()])
            m_orders = act.get("market", []) if act else []
            m_str = str(m_orders[:3]) + ("..." if len(m_orders) > 3 else "")
            
            if h in [0, 23] or m_orders:
                print(f"D{d:02d} | H{h:02d} | ${bank:7,.0f} | {hands:5d} | {quads:5d} | {cows:4d} | {sheep:5d} | {crops_str:<28} | {m_str:<35}")

if __name__ == "__main__":
    trace_top_replay("103388734", 1) # $162.8k
