from kaggle_environments import make

def run_match(agent1, agent2):
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run([agent1, agent2])
    rewards = [env.steps[-1][0]['reward'], env.steps[-1][1]['reward']]
    return rewards

if __name__ == "__main__":
    agent = "submission_v104_quote_priority.py"
    opponents = ["pass", "random"]
    
    print("Testing V104:")
    for opp in opponents:
        try:
            r = run_match(agent, opp)
            print(f"V104 vs {opp}: {r[0]} - {r[1]}")
        except Exception as e:
            print(f"Error vs {opp}: {e}")
