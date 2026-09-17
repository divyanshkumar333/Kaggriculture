import json
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=True)
    
    # 007 vs v060 Melon Frontrunner
    env.run(['experiments/007_ultimate_router/main.py', 'agents/v060_melon_frontrunner.py'])
    
    print("Match finished.")
    steps = env.steps
    p0_score = steps[-1][0].reward
    p1_score = steps[-1][1].reward
    print(f"P0 (007) Score: {p0_score}")
    print(f"P1 (v060) Score: {p1_score}")
    
    # Let's find the first step where P1's money exceeds P0's money by > 500
    for i, step in enumerate(steps):
        if step[0].observation is None: continue
        p0_farms = step[0].observation['farms']
        if len(p0_farms) < 2: continue
        
        m0 = p0_farms[0]['money']
        m1 = p0_farms[1]['money']
        if m1 - m0 > 1000:
            print(f"Divergence found at step {i} (Day {step[0].observation['day']} Hour {step[0].observation['hour']})")
            print(f"P0 Money: {m0}, P1 Money: {m1}")
            
            # Print recent actions
            print(f"P1 Action: {steps[i-1][1].action}")
            print(f"P0 Action: {steps[i-1][0].action}")
            
            # Print market state
            print(f"Market: {step[0].observation['market']['prices']}")
            break

if __name__ == "__main__":
    main()
