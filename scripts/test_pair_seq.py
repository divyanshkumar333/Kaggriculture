import sys
import os
import json
from kaggle_environments import make

def run_fast_tournament_seq(cand_path, opp_paths, seeds=4):
    wins = 0
    losses = 0
    margin = 0
    
    for opp_path in opp_paths:
        for seed in range(1337, 1337+seeds):
            for reverse in [False, True]:
                env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed})
                agents = [opp_path, cand_path] if reverse else [cand_path, opp_path]
                steps = env.run(agents)
                
                final_state = steps[-1]
                p0_r = final_state[0]['reward'] or 0
                p1_r = final_state[1]['reward'] or 0
                
                cand_r = p1_r if reverse else p0_r
                opp_r = p0_r if reverse else p1_r
                
                if cand_r > opp_r:
                    wins += 1
                elif opp_r > cand_r:
                    losses += 1
                
                margin += (cand_r - opp_r)
                
    return wins, losses, margin

if __name__ == '__main__':
    cand_path = sys.argv[1]
    opp_path = sys.argv[2]
    seeds = int(sys.argv[3])
    
    w, l, m = run_fast_tournament_seq(cand_path, [opp_path], seeds=seeds)
    print(f"Wins: {w}, Losses: {l}, Margin: {m}")
