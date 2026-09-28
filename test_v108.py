import sys
from kaggle_environments import make

def run_match():
    env = make("kaggriculture", debug=True, configuration={"episodeSteps": 720})
    print("Running V108 (162k Trace + Quote Priority Chassis) vs V104 (Original Quote Priority)...")
    try:
        env.run(["submission_v108_injected_162k.py", "submission_v104_quote_priority.py"])
        
        final_state = env.steps[-1]
        
        # P0 is V108, P1 is V104
        p0_reward = final_state[0].reward
        p1_reward = final_state[1].reward
        
        print(f"V108 (162k Trace) Cash: {p0_reward}")
        print(f"V104 (Original)   Cash: {p1_reward}")
        
        if p0_reward > p1_reward:
            print(">>> V108 WINS! <<<")
        elif p1_reward > p0_reward:
            print(">>> V104 WINS! <<<")
        else:
            print(">>> TIE <<<")
            
        return env
    except BaseException as e:
        if "Unknown game" in str(e):
            pass
        else:
            raise

if __name__ == "__main__":
    run_match()
