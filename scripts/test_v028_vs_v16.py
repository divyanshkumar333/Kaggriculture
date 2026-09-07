import os
from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def run():
    agent1 = load_agent("agents/v028_notebook_1c4s_opening.py")
    agent2 = load_agent("agents/public_v16_rc5.py")
    
    seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    a1_wins = 0
    a2_wins = 0
    a1_money = []
    a2_money = []
    
    for s in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([agent1, agent2])
        r1 = env.steps[-1][0].reward or 0
        r2 = env.steps[-1][1].reward or 0
        a1_money.append(r1)
        a2_money.append(r2)
        if r1 > r2: a1_wins += 1
        elif r2 > r1: a2_wins += 1
        print(f"Seed {s} P0=v028: {r1} vs P1=v16: {r2} (Diff: {r1-r2})")
        
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([agent2, agent1])
        r2 = env.steps[-1][0].reward or 0
        r1 = env.steps[-1][1].reward or 0
        a1_money.append(r1)
        a2_money.append(r2)
        if r1 > r2: a1_wins += 1
        elif r2 > r1: a2_wins += 1
        print(f"Seed {s} P0=v16: {r2} vs P1=v028: {r1} (Diff: {r1-r2})")

    print(f"Wins: V028={a1_wins}, V16={a2_wins}")
    print(f"Mean: V028={sum(a1_money)/len(a1_money)}, V16={sum(a2_money)/len(a2_money)}")

if __name__ == '__main__':
    run()
