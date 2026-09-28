import sys
from kaggle_environments import make

def run_match():
    env = make("kaggriculture", debug=True, configuration={"episodeSteps": 720})
    print("Running V109 (162k Full Override) vs V104 (Original Quote Priority)...")
    try:
        env.run(["submission_v109_full_162k.py", "submission_v104_quote_priority.py"])
        
        final_state = env.steps[-1]
        
        # P0 is V109, P1 is V104
        p0_reward = final_state[0].reward
        p1_reward = final_state[1].reward
        
        print(f"V109 (162k Override) Cash: {p0_reward}")
        print(f"V104 (Original)      Cash: {p1_reward}")
        
        # Save replay for debugging
        import json
        with open("scratch/v109_replay.json", "w") as f:
            json.dump(env.toJSON(), f)
            
        print("Saved scratch/v109_replay.json")
        
        return env
    except BaseException as e:
        if "Unknown game" in str(e):
            pass
        else:
            raise

if __name__ == "__main__":
    run_match()
