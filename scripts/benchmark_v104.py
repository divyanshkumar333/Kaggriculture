from kaggle_environments import make
import json

def run_match(agent1, agent2):
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([agent1, agent2])
    rewards = [env.steps[-1][0]['reward'], env.steps[-1][1]['reward']]
    return rewards

if __name__ == "__main__":
    opponents = ["agents/014_robust_trace.py", "agents/v057_deep_frontrun.py"]
    
    print("Testing V104 vs Opponents:")
    for opp in opponents:
        r = run_match("agents/v104_quote_priority.py", opp)
        print(f"V104 vs {opp}: {r[0]} - {r[1]} -> {'Win' if r[0] > r[1] else 'Loss'}")
        
    print("\nTesting 2945 vs Opponents:")
    for opp in opponents:
        r = run_match("agents/the_2945_farm.py", opp)
        print(f"2945 vs {opp}: {r[0]} - {r[1]} -> {'Win' if r[0] > r[1] else 'Loss'}")
