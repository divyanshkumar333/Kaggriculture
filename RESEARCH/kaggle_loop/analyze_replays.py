import json
import glob
import sys
import collections

def analyze_actions(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    
    steps = data.get("steps", [])
    if not steps: return
    
    final_step = steps[-1]
    p0_reward = final_step[0].get("reward", 0)
    p1_reward = final_step[1].get("reward", 0)
    
    winner = 0 if p0_reward > p1_reward else 1
    
    print(f"\n--- {file_path} --- Winner: Player {winner} (Score {max(p0_reward, p1_reward)})")
    
    purchases = collections.Counter()
    plantings = collections.Counter()
    
    # We trace all actions the winner took
    for step_idx, step in enumerate(steps):
        # player action is stored in step[0]["action"] (for p0) or step[1]["action"]
        if step_idx == 0: continue
        
        # In Kaggle replays, step[i]["action"] is the action taken by player i in the previous step
        # Wait, the action taken at step N is applied to compute step N+1.
        action = step[winner].get("action", {})
        if not action or not isinstance(action, dict):
            continue
            
        # Parse market actions
        for m_act in action.get("market", []):
            if m_act and m_act[0] == "BUY_SEED":
                purchases[m_act[1]] += m_act[2]
            elif m_act and m_act[0] == "BUY_ANIMAL":
                purchases[m_act[1]] += m_act[2]
            elif m_act and m_act[0] == "BUY_LAND":
                purchases["LAND"] += 1
                
        # Parse farmer actions
        f_act = action.get("farmer", [])
        if f_act and f_act[0] == "PLANT":
            plantings[f_act[1]] += 1
            
        for h_act in action.get("hands", []):
            if h_act and h_act[0] == "PLANT":
                plantings[h_act[1]] += 1
                
    print(f"Purchases: {dict(purchases)}")
    print(f"Plantings: {dict(plantings)}")

if __name__ == "__main__":
    replays = glob.glob("episode-*.json")
    for r in replays:
        analyze_actions(r)
