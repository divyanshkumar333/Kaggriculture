from kaggle_environments import make
import numpy as np

def evaluate_tape():
    agent = "agents/generated_premium_route_1.py"
    opp = "pass"
    
    scores = []
    for i in range(10):
        try:
            env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
            env.run([agent, opp])
            r = env.steps[-1][0]['reward']
            scores.append(r)
            print(f"Seed {i} Score: {r}")
        except Exception as e:
            pass
            
    print(f"Mean: {np.mean(scores)}, Max: {np.max(scores)}, Min: {np.min(scores)}")

if __name__ == "__main__":
    evaluate_tape()
