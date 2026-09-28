from kaggle_environments import make
import json
from pathlib import Path

def run_match():
    print("Running V104 vs 2945 Farm...")
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    
    # Run a match
    env.run(["agents/v104_quote_priority.py", "agents/the_2945_farm.py"])
    
    steps = env.steps
    rewards = [steps[-1][0]['reward'], steps[-1][1]['reward']]
    
    print(f"P0 (V104): {rewards[0]}")
    print(f"P1 (2945 Farm): {rewards[1]}")
    
    if rewards[1] > rewards[0]:
        print("2945 Farm wins!")
    else:
        print("V104 wins!")
        
    out_dir = Path("RESEARCH/kaggle_loop/market_lab")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "v104_vs_2945.json", "w") as f:
        json.dump(env.toJSON(), f)

if __name__ == "__main__":
    run_match()
