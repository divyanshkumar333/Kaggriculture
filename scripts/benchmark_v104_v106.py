import sys
import os
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')
from kaggle_environments import make
import importlib.util

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v104 = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py")
v106 = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\v106_relaxed_dynamic.py")

v104_wins = 0
v106_wins = 0
v104_total = 0
v106_total = 0

print(f"{'Seed':>5} {'V104 (P0)':>10} {'V106 (P1)':>10} | {'Winner':>6}")
print("-" * 40)

for i in range(10):
    seed = 200 + i
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    
    env.run([v104, v106])
    
    final = env.steps[-1][0]['observation']['farms']
    p0 = final[0]['money']
    p1 = final[1]['money']
    
    v104_total += p0
    v106_total += p1
    
    winner = "V104" if p0 > p1 else ("V106" if p1 > p0 else "TIE")
    if p0 > p1: v104_wins += 1
    elif p1 > p0: v106_wins += 1
    
    print(f"{seed:5d} {p0:10.0f} {p1:10.0f} | {winner:>6}")

print("-" * 40)
print(f"V104 Wins: {v104_wins}")
print(f"V106 Wins: {v106_wins}")
print(f"V104 Avg: {v104_total/10:.0f}")
print(f"V106 Avg: {v106_total/10:.0f}")
