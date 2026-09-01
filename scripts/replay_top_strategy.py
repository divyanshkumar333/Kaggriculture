import json
from kaggle_environments import make

def test_exact_replay():
    replay_path = "kaggle_episodes/episode-103388734-replay.json"
    with open(replay_path, "r") as f:
        data = json.load(f)
        
    steps = data["steps"]
    print(f"Replay has {len(steps)} steps.")
    
    # Extract actions for both players
    p0_actions = []
    p1_actions = []
    for s in steps:
        a0 = s[0].get("action")
        a1 = s[1].get("action")
        p0_actions.append(a0 if isinstance(a0, dict) else {"farmer": ["PASS"], "hands": [], "market": []})
        p1_actions.append(a1 if isinstance(a1, dict) else {"farmer": ["PASS"], "hands": [], "market": []})
        
    # Build callable agents
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
    env.run([agent_p0, agent_p1])
    
    final_step = env.steps[-1]
    print("\n--- LOCAL SIMULATION REPLAY RESULT ---")
    print(f"Player 0 Reward: ${final_step[0]['reward']:,} | Status: {final_step[0]['status']}")
    print(f"Player 1 Reward: ${final_step[1]['reward']:,} | Status: {final_step[1]['status']}")
    
    # Check if there are any discrepancies
    p0_obs_final = final_step[0]["observation"]["farms"][0]
    p1_obs_final = final_step[0]["observation"]["farms"][1]
    print(f"P0 Final Bank: ${p0_obs_final['money']:,}")
    print(f"P1 Final Bank: ${p1_obs_final['money']:,}")

if __name__ == "__main__":
    test_exact_replay()
