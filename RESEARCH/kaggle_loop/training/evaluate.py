from kaggle_environments import make
import sys

def evaluate():
    try:
        print("Initializing environment...")
        env = make("kaggriculture", configuration={"episodeSteps": 150}, debug=True)
        
        # Match 1: Hybrid Agent vs 001 Meta Classifier
        print("Running match 1: Hybrid Agent vs 001 Meta Classifier")
        env.run(["RESEARCH/kaggle_loop/training/hybrid_agent.py", "experiments/meta_classifier/main.py"])
        
        final_step = env.steps[-1]
        p0_reward = final_step[0].reward
        p1_reward = final_step[1].reward
        print(f"Match 1 complete. P0 (Hybrid): {p0_reward}, P1 (001 Meta): {p1_reward}")
        
        # Match 2: Hybrid Agent vs Random
        print("Running match 2: Hybrid Agent vs Random")
        env.run(["RESEARCH/kaggle_loop/training/hybrid_agent.py", "random"])
        
        final_step = env.steps[-1]
        p0_reward = final_step[0].reward
        p1_reward = final_step[1].reward
        print(f"Match 2 complete. P0 (Hybrid): {p0_reward}, P1 (Random): {p1_reward}")
        
        print("Evaluation complete.")
    except Exception as e:
        print(f"Evaluation FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    evaluate()
