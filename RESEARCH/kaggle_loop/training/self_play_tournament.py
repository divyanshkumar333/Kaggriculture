import os
import time
import json
import itertools
from multiprocessing import Pool
from collections import defaultdict
from kaggle_environments import make

AGENTS = [
    "agents/v051_v16_lookahead30_final.py",
    "agents/v025_a_aggressive_cows.py",
    "agents/v027_hierarchical_meta.py",
    "agents/v057_generalized_spoiler.py",
    "agents/v059_strawberry_flywheel.py",
    "agents/v060_melon_frontrunner.py",
    "agents/v063_meta_router.py"
]

SEEDS = list(range(10)) # 10 seeds per pairing

def run_match(args):
    agent0, agent1, seed = args
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    env.run([agent0, agent1])
    
    score0 = env.steps[-1][0].reward or 0
    score1 = env.steps[-1][1].reward or 0
    
    name0 = os.path.basename(agent0)
    name1 = os.path.basename(agent1)
    
    return {
        "agent0": name0,
        "agent1": name1,
        "score0": score0,
        "score1": score1,
        "seed": seed,
        "margin": score0 - score1,
        "win0": 1 if score0 > score1 else (0.5 if score0 == score1 else 0),
        "win1": 1 if score1 > score0 else (0.5 if score0 == score1 else 0)
    }

def main():
    print("Building Matchups...")
    # Generate all pairings (including self-play!)
    matchups = []
    for a0, a1 in itertools.product(AGENTS, AGENTS):
        for seed in SEEDS:
            matchups.append((a0, a1, seed))
            
    print(f"Total Matches: {len(matchups)}")
    
    start_time = time.time()
    with Pool(processes=os.cpu_count() or 4) as pool:
        results = pool.map(run_match, matchups)
        
    print(f"Tournament finished in {time.time() - start_time:.1f} seconds")
    
    # Calculate Elo / Win Rates
    stats = defaultdict(lambda: {"wins": 0, "matches": 0, "score_sum": 0})
    
    for r in results:
        a0, a1 = r["agent0"], r["agent1"]
        
        stats[a0]["matches"] += 1
        stats[a0]["wins"] += r["win0"]
        stats[a0]["score_sum"] += r["score0"]
        
        stats[a1]["matches"] += 1
        stats[a1]["wins"] += r["win1"]
        stats[a1]["score_sum"] += r["score1"]
        
    print("\n--- TOURNAMENT RESULTS ---")
    sorted_agents = sorted(stats.keys(), key=lambda x: stats[x]["wins"] / stats[x]["matches"], reverse=True)
    
    for rank, agent in enumerate(sorted_agents):
        s = stats[agent]
        win_rate = s["wins"] / s["matches"]
        avg_score = s["score_sum"] / s["matches"]
        print(f"{rank+1}. {agent:35s} | Win Rate: {win_rate*100:5.1f}% | Avg Score: {avg_score:8.0f}")
        
    with open("RESEARCH/kaggle_loop/training/tournament_results.json", "w") as f:
        json.dump({"stats": stats, "results": results}, f, indent=2)
        
if __name__ == "__main__":
    main()
