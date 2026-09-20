import sys
import json

def analyze_replay(filepath):
    with open(filepath, "r") as f:
        replay = json.load(f)
    
    steps = replay.get("steps", [])
    if not steps:
        print("No steps found in replay.")
        return

    print(f"Analyzing {filepath}")
    diverged = False
    for i, step in enumerate(steps):
        if len(step) < 2: continue
        obs0 = step[0].get("observation", {})
        
        # Check farms
        farms = obs0.get("farms", [])
        if len(farms) < 2: continue
        
        f0, f1 = farms[0], farms[1]
        
        # Compare strategic macro-state
        m0, m1 = f0.get("money", 0), f1.get("money", 0)
        h0, h1 = len(f0.get("hands", [])), len(f1.get("hands", []))
        
        # Private shed state is not in obs0 for player 1, but we can look at step[1] for player 1's private state
        obs1 = step[1].get("observation", {})
        shed0 = obs0.get("private", {}).get("shed", {})
        shed1 = obs1.get("private", {}).get("shed", {})
        
        if (m0 != m1 or h0 != h1 or shed0 != shed1) and not diverged:
            print(f"\n--- FIRST DIVERGENCE AT TURN {i} ---")
            print(f"Player 0 (Cash: {m0}, Hands: {h0}, Shed: {shed0})")
            print(f"Player 1 (Cash: {m1}, Hands: {h1}, Shed: {shed1})")
            diverged = True
            
        if i in [0, 24, 48, 72, 96, 120, 144, 200, 300, 400, 500, 600, 648, 696, 719]:
            print(f"Turn {i}: P0_Cash={m0} P1_Cash={m1} | P0_Hands={h0} P1_Hands={h1}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_first_divergence.py <replay.json>")
    else:
        analyze_replay(sys.argv[1])
