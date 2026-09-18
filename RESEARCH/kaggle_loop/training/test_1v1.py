import sys
from kaggle_environments import make

def run(agent1, agent2, num_matches=3):
    wins_1 = 0
    wins_2 = 0
    score_1 = 0
    score_2 = 0
    
    for i in range(num_matches):
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
        env.run([agent1, agent2])
        s1 = env.steps[-1][0].reward or 0
        s2 = env.steps[-1][1].reward or 0
        score_1 += s1
        score_2 += s2
        if s1 > s2:
            wins_1 += 1
        elif s2 > s1:
            wins_2 += 1
        print(f"Match {i+1}: A1={s1} A2={s2}")
        
    print(f"Wins: A1={wins_1} A2={wins_2}")
    print(f"Avg Score: A1={score_1/num_matches:.1f} A2={score_2/num_matches:.1f}")

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
