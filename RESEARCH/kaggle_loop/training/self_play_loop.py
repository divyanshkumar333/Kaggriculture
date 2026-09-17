import os
import time
import subprocess
import json
from kaggle_environments import make

def generate_matches(num_matches=10):
    print(f"Generating {num_matches} self-play matches...")
    env = make("kaggriculture", debug=False)
    
    agent_path = "experiments/002_counterfactual_agent/main.py"
    opponents = ["random", "agents/v057_generalized_spoiler.py"]
    
    for i in range(num_matches):
        opp = opponents[i % len(opponents)]
        print(f"  Match {i+1}/{num_matches}: 002 vs {opp}")
        env.run([agent_path, opp])
        
        # Save replay temporarily
        out_path = f"scratch/self_play_{int(time.time())}.json"
        with open(out_path, "w") as f:
            json.dump(env.toJSON(), f)

def extract_and_append_data():
    print("Extracting features from new replays...")
    # This would call a parser to append to CSV
    pass

def train_model():
    print("Retraining XGBoost Value Model...")
    subprocess.run([".venv\\Scripts\\python", "RESEARCH/kaggle_loop/training/train_xgboost.py"])

def run_loop(duration_hours=2):
    end_time = time.time() + duration_hours * 3600
    iteration = 1
    
    while time.time() < end_time:
        print(f"\n=== Training Iteration {iteration} ===")
        print(f"Time remaining: {(end_time - time.time())/60:.1f} minutes")
        
        generate_matches(10)
        train_model()
        
        iteration += 1
        
    print("Training loop complete!")

if __name__ == "__main__":
    os.makedirs("scratch", exist_ok=True)
    run_loop(duration_hours=2)
