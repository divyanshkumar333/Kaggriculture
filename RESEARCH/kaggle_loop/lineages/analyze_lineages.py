import json
import glob
import pandas as pd
from collections import defaultdict
import os

def analyze():
    # Load meta
    meta_path = 'RESEARCH/kaggle_loop/training/datasets/matches_meta.csv'
    if not os.path.exists(meta_path):
        return
        
    df = pd.read_csv(meta_path)
    
    # We want to identify the most successful "unknown" agents.
    # What agents are dominating? We can look at the average score of each team/submission!
    print("Loading episodes...")
    
    agent_stats = defaultdict(lambda: {"wins": 0, "matches": 0, "score_sum": 0})
    
    for i, row in df.iterrows():
        ep_id = row['episode_id']
        t0 = row['player_0_team']
        t1 = row['player_1_team']
        s0 = row['player_0_score']
        s1 = row['player_1_score']
        
        agent_stats[t0]["matches"] += 1
        agent_stats[t0]["score_sum"] += s0
        agent_stats[t0]["wins"] += 1 if s0 > s1 else (0.5 if s0 == s1 else 0)
        
        agent_stats[t1]["matches"] += 1
        agent_stats[t1]["score_sum"] += s1
        agent_stats[t1]["wins"] += 1 if s1 > s0 else (0.5 if s1 == s0 else 0)
        
    print("\n--- TOP KAGGLE AGENTS (By Win Rate) ---")
    sorted_teams = sorted(agent_stats.keys(), key=lambda t: (agent_stats[t]["wins"]/agent_stats[t]["matches"], agent_stats[t]["matches"]), reverse=True)
    
    for team in sorted_teams[:20]:
        st = agent_stats[team]
        if st["matches"] >= 5:
            wr = st["wins"] / st["matches"]
            avg = st["score_sum"] / st["matches"]
            print(f"{team:30s} | Matches: {st['matches']:3d} | WR: {wr*100:5.1f}% | Avg: {avg:8.0f}")

if __name__ == "__main__":
    analyze()
