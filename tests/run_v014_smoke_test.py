import json
from kaggle_environments import make
import numpy as np

variants = [
    ("A: Control", "agents/v014_a_control.py"),
    ("B: Deadline", "agents/v014_b_deadline_only.py"),
    ("C: Economic", "agents/v014_c_economic_only.py"),
    ("D: Combined", "agents/v014_d_combined.py"),
]
seeds = [101, 102, 103, 104, 105]

print("Running 5-game smoke test for V014 (vs random)...")

results = {name: [] for name, _ in variants}

for name, path in variants:
    print(f"\n--- Testing {name} ---")
    for seed in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        _ = env.run([path, "random"])
        
        final_state = env.steps[-1]
        p0_reward = final_state[0].reward
        status = final_state[0].status
        results[name].append(p0_reward)
        
        print(f"Seed {seed}: ${p0_reward:,.2f} ({status})")

print("\n=== Smoke Test Summary ===")
for name, _ in variants:
    scores = results[name]
    avg = np.mean(scores)
    print(f"{name:15}: ${avg:,.2f}")
