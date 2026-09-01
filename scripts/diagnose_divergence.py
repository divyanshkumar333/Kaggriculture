import json
from kaggle_environments import make

def diagnose():
    replay_path = "kaggle_episodes/episode-103388734-replay.json"
    with open(replay_path, "r") as f:
        data = json.load(f)
        
    orig_steps = data["steps"]
    
    p0_actions = []
    p1_actions = []
    for s in orig_steps:
        a0 = s[0].get("action")
        a1 = s[1].get("action")
        p0_actions.append(a0 if isinstance(a0, dict) else {"farmer": ["PASS"], "hands": [], "market": []})
        p1_actions.append(a1 if isinstance(a1, dict) else {"farmer": ["PASS"], "hands": [], "market": []})
        
    def agent_p0(obs):
        step = obs["step"]
        if step < len(p0_actions):
            return p0_actions[step]
        return {"farmer": ["PASS"], "hands": [], "market": []}
        
    def agent_p1(obs):
        step = obs["step"]
        if step < len(p1_actions):
            return p1_actions[step]
        return {"farmer": ["PASS"], "hands": [], "market": []}
        
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    
    # Run step-by-step
    env.reset()
    
    divergences = []
    
    for t in range(720):
        # Current observation in local env
        obs_local = env.state[0]["observation"]
        obs_orig = orig_steps[t][0]["observation"]
        
        p1_m_local = obs_local["farms"][1]["money"]
        p1_m_orig = obs_orig["farms"][1]["money"]
        
        p1_hands_local = len(obs_local["farms"][1]["hands"])
        p1_hands_orig = len(obs_orig["farms"][1]["hands"])
        
        # Check town shops
        shops_local = obs_local.get("town", {}).get("unlocked_shops", [])
        shops_orig = obs_orig.get("town", {}).get("unlocked_shops", [])
        
        if abs(p1_m_local - p1_m_orig) > 10 and len(divergences) < 15:
            divergences.append({
                "step": t,
                "day": t // 24,
                "hour": t % 24,
                "money_local": p1_m_local,
                "money_orig": p1_m_orig,
                "hands_local": p1_hands_local,
                "hands_orig": p1_hands_orig,
                "shops_local": shops_local,
                "shops_orig": shops_orig,
            })
            
        env.step([p0_actions[t], p1_actions[t]])
        
    print("=== FIRST 15 DIVERGENCE POINTS ===")
    for d in divergences:
        print(f"Step {d['step']:3d} (Day {d['day']:2d}, Hr {d['hour']:2d}): Local Bank=${d['money_local']:.0f} vs Orig Bank=${d['money_orig']:.0f} (Diff: ${d['money_local']-d['money_orig']:+.0f})")
        print(f"   Hands Local: {d['hands_local']} vs Orig: {d['hands_orig']}")
        print(f"   Shops Local: {d['shops_local']}")
        print(f"   Shops Orig:  {d['shops_orig']}")

if __name__ == "__main__":
    diagnose()
