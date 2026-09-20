import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def main():
    ap = argparse.ArgumentParser(description="Run a counterfactual match from a specific step in a replay.")
    ap.add_argument("replay", help="Path to replay JSON file")
    ap.add_argument("step", type=int, help="Step index to branch from")
    ap.add_argument("agent_a", help="Agent A to run from the branch point")
    ap.add_argument("agent_b", help="Agent B to run from the branch point")
    args = ap.parse_args()

    print(f"Loading replay: {args.replay}")
    with open(args.replay, "r") as f:
        replay_data = json.load(f)

    cfg = replay_data.get("configuration", {})
    steps = replay_data.get("steps", [])

    if args.step >= len(steps):
        print(f"Error: Requested step {args.step} is beyond replay length {len(steps)}.")
        return 1

    print(f"Branching at step {args.step}...")
    branch_steps = steps[:args.step + 1]

    # Silence output during Kaggle make and run
    import os
    from contextlib import redirect_stdout, redirect_stderr
    from kaggle_environments import make

    print(f"Initializing Kaggle environment with injected state...")
    env = make("kaggriculture", configuration=cfg, steps=branch_steps, debug=False)
    
    print(f"Running rest of the game with {args.agent_a} and {args.agent_b}...")
    
    try:
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([args.agent_a, args.agent_b])
    except Exception as e:
        print(f"Simulation failed: {e}")
        return 1

    final_state = env.steps[-1]
    p0_reward = final_state[0].reward or 0
    p1_reward = final_state[1].reward or 0

    print("\n================ COUNTERFACTUAL RESULT ================")
    print(f"Agent A: ${p0_reward:,.0f}")
    print(f"Agent B: ${p1_reward:,.0f}")
    
    delta = p0_reward - p1_reward
    if delta > 0:
        print(f"Agent A wins by ${delta:,.0f}")
    elif delta < 0:
        print(f"Agent B wins by ${-delta:,.0f}")
    else:
        print("TIE")
    print("=======================================================")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
