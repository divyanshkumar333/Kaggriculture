import json
import sys

def main(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    steps = data.get('steps', [])
    info = data.get('info', {})
    
    print(f"Team Names: {info.get('TeamNames')}")
    
    final_state = steps[-1]
    p0_reward = final_state[0]['reward']
    p1_reward = final_state[1]['reward']
    print(f"Final Score: P0 = {p0_reward}, P1 = {p1_reward}")
    
    # Let's see some basic stats at step 600 or end of game
    for step_num in [300, 600, len(steps)-1]:
        if step_num < len(steps):
            state = steps[step_num][0]['observation']
            farms = state['farms']
            print(f"\n--- STEP {step_num} ---")
            for i, f in enumerate(farms):
                print(f"P{i} Cash: {f['money']}, Hands: {f.get('hires_today', 0)}")

if __name__ == '__main__':
    main(sys.argv[1])
