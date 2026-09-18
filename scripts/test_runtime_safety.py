import sys
import traceback
from kaggle_environments import make

def test_agent_safety(agent_path, opponent="random"):
    print(f"=== TESTING {agent_path} vs {opponent} ===")
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
        # debug=True ensures exceptions fail loudly instead of returning PASS
        
        # We also need to verify that it actually runs 720 steps and doesn't end early
        # unless it's a tie/win
        
        out = env.run([agent_path, opponent])
        
        final_step = env.steps[-1]
        
        p1_status = final_step[0].status
        p2_status = final_step[1].status
        
        if p1_status == "ERROR" or p1_status == "INVALID":
            print(f"FAILED: Agent {agent_path} threw {p1_status}")
            if final_step[0].observation.get("errors"):
                print(final_step[0].observation["errors"])
            sys.exit(1)
            
        print(f"SUCCESS: Agent survived {len(env.steps)} steps with status {p1_status}.")
        print(f"Score: {final_step[0].reward}")
        
    except Exception as e:
        print(f"FAILED: Fatal exception during run:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_runtime_safety.py <agent_path>")
        sys.exit(1)
        
    test_agent_safety(sys.argv[1])
