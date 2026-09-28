import sys
from kaggle_environments import make

def run_match():
    env = make("kaggriculture", debug=True, configuration={"episodeSteps": 720})
    print("Running V106 (Premium Frontrunner) vs V104 (Quote Priority Animal Heavy)...")
    try:
        env.run(["submission_v106_premium_frontrunner.py", "submission_v104_quote_priority.py"])
        
        final_state = env.steps[-1]
        
        # P0 is V106, P1 is V104
        p0_reward = final_state[0].reward
        p1_reward = final_state[1].reward
        
        print(f"V106 (Premium) Cash: {p0_reward}")
        print(f"V104 (Animal)  Cash: {p1_reward}")
        
        if p0_reward > p1_reward:
            print(">>> V106 WINS! <<<")
        elif p1_reward > p0_reward:
            print(">>> V104 WINS! <<<")
        else:
            print(">>> TIE <<<")
            
        return env
    except BaseException as e:
        if "Unknown game" in str(e):
            pass # OpenSpiel known artifact
        else:
            raise

if __name__ == "__main__":
    run_match()
