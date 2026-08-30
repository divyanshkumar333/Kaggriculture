import json

def trace_opponent_bootstrap(ep_file, opp_p):
    with open(ep_file, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    print("=" * 100)
    print(f"BOOTSTRAP TRACE: {ep_file} for Player {opp_p}")
    print("=" * 100)
    
    for day in range(12):
        print(f"\n--- DAY {day} ---")
        for h in range(24):
            s_idx = day * 24 + h
            if s_idx >= len(steps): break
            st = steps[s_idx]
            obs = st[0]["observation"]
            opp_farm = obs["farms"][opp_p]
            act = st[opp_p].get("action")
            
            # Print non-trivial actions or market actions
            farmer_act = act.get("farmer", []) if isinstance(act, dict) else []
            market_act = act.get("market", []) if isinstance(act, dict) else []
            hands_act = act.get("hands", []) if isinstance(act, dict) else []
            
            non_pass_hands = [a for a in hands_act if a[0] not in ["PASS", "NORTH", "SOUTH", "EAST", "WEST"]]
            
            if market_act or (farmer_act and farmer_act[0] not in ["PASS", "NORTH", "SOUTH", "EAST", "WEST"]) or non_pass_hands or h == 0:
                print(f"  Hour {h:2d} | Money: ${opp_farm['money']:6,.0f} | Hands: {len(opp_farm.get('hands', []))} | Farmer: {farmer_act} | Mkt: {market_act} | KeyHands: {non_pass_hands}")

if __name__ == "__main__":
    trace_opponent_bootstrap("kaggle_episodes/sub_55899068/episode-103533735-replay.json", 1)
