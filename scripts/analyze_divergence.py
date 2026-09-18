import json
import glob
import os

def parse_action_string(action_str):
    if not isinstance(action_str, str): return []
    # Actions are stringified JSON arrays
    try:
        return json.loads(action_str)
    except:
        return []

def main():
    files = glob.glob("episode-*-replay.json")
    print(f"Found {len(files)} replays to analyze.")
    
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        steps = data.get("steps", [])
        if not steps: continue
        
        final_p1 = steps[-1][0].get("reward", 0)
        final_p2 = steps[-1][1].get("reward", 0)
        
        winner_idx = 0 if final_p1 >= final_p2 else 1
        loser_idx = 1 - winner_idx
        
        winner_reward = max(final_p1, final_p2)
        loser_reward = min(final_p1, final_p2)
        
        # Only analyze if the winner scored highly (> 80k) to filter out bad games
        if winner_reward < 80000:
            continue
            
        print(f"\n--- {fpath} ---")
        print(f"Winner (Seat {winner_idx}): {winner_reward} | Loser: {loser_reward}")
        
        # Analyze early macro opening (Days 0 - 3)
        print("WINNER OPENING (Day 0):")
        
        day_0_hires = 0
        day_0_market = []
        
        for step_num, step_data in enumerate(steps):
            obs = step_data[0]["observation"]
            if obs["step"] == 0:
                pass # Initial state
                
            # Kaggle stores actions taken IN PREVIOUS STEP inside the CURRENT step's observation structure or in the agent state
            # Actually, `step_data[0]["action"]` is the action player 0 took AT THIS STEP.
            
            if obs["step"] < 24: # Day 0
                winner_action_dict = step_data[winner_idx].get("action", {})
                if not winner_action_dict: continue
                
                market_ops = winner_action_dict.get("market", [])
                for op in market_ops:
                    if op[0] == "HIRE": day_0_hires += 1
                    else: day_0_market.append(op)
                    
            if obs["step"] == 24:
                break
                
        print(f"Day 0 Hires: {day_0_hires}")
        print(f"Day 0 Market Ops: {day_0_market}")

if __name__ == "__main__":
    main()
