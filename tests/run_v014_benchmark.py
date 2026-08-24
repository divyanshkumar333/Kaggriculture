import sys
import json
from kaggle_environments import make

def main():
    if len(sys.argv) != 5:
        print("Usage: python run_v014_benchmark.py <variant_path> <opponent> <seed> <output_json>")
        sys.exit(1)
        
    variant_path = sys.argv[1]
    opponent = sys.argv[2]
    seed = int(sys.argv[3])
    output_json = sys.argv[4]

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    _ = env.run([variant_path, opponent])
    
    final_state = env.steps[-1]
    p0_reward = final_state[0].reward
    
    # Very basic stats extraction
    # We can write a dedicated analyzer script for V014 to parse replay files later if needed,
    # but for now, just record the final reward.
    result = {
        "variant": variant_path,
        "opponent": opponent,
        "seed": seed,
        "reward": p0_reward
    }
    
    with open(output_json, "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
