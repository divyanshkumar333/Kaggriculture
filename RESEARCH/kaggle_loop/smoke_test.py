from kaggle_environments import make
import sys

try:
    print("Initializing environment...")
    env = make("kaggriculture", configuration={"episodeSteps": 100}, debug=True)
    print("Running match: Meta Classifier vs random")
    env.run(["experiments/meta_classifier/main.py", "random"])
    
    final_step = env.steps[-1]
    p0_reward = final_step[0].reward
    p1_reward = final_step[1].reward
    print(f"Match complete. P0 (Meta): {p0_reward}, P1 (Random): {p1_reward}")
    print("Smoke test PASSED!")
except Exception as e:
    print(f"Smoke test FAILED: {e}")
    sys.exit(1)
