import random
import multiprocessing
from kaggle_environments import make

AGENTS = [
    'agents/v065_ablation_melon_only.py',
    'agents/v066_ablation_strawberry_only.py',
    'agents/v067_ablation_depth_18.py',
    'agents/v068_frontrun_plus_two.py',
    'agents/v069_hybrid_spoiler.py'
]

CONTROLS = [
    'agents/public_v16_rc5.py',
    'agents/v057_generalized_spoiler.py'
]

def run_match(args):
    agent, opp, seed = args
    env = make("kaggriculture", configuration={"randomSeed": seed, "episodeSteps": 720})
    env.run([agent, opp])
    rewards = env.steps[-1][0].reward, env.steps[-1][1].reward
    return agent, opp, rewards[0], rewards[1]

if __name__ == "__main__":
    tasks = []
    for agent in AGENTS:
        for opp in CONTROLS:
            # Run 3 seeds per matchup to get a rough average
            for i in range(3):
                tasks.append((agent, opp, random.randint(0, 1000000)))
                
    with multiprocessing.Pool() as pool:
        results = pool.map(run_match, tasks)
        
    scores = {}
    for a, o, r1, r2 in results:
        scores.setdefault(a, {}).setdefault(o, []).append(r1)
        
    for a in AGENTS:
        print(f"--- {a} ---")
        for o in CONTROLS:
            avg = sum(scores[a][o]) / len(scores[a][o])
            print(f"vs {o}: {avg:.1f}")
        print()
