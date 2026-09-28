import os
import json
import numpy as np
from kaggle_environments import make

def run_benchmarks():
    agents = {
        'V104_Current': 'submission_v104_quote_priority.py',
        '162k_Trace': 'agents/extracted_162k_route.py',
        '190k_Trace': 'agents/submission_v112_190k_trace.py',
        'Premium_Only': 'agents/generated_premium_route_1.py',
        'Default_Route2': 'agents/forced_routes/v104_route_2.py' # 2 is a known default route
    }
    
    opponents = ['agents/public_v16_rc5.py'] # Just one opponent for quick turnaround
    seeds = [42, 43, 44]
    
    results = {}
    
    for agent_name, agent_path in agents.items():
        if not os.path.exists(agent_path): 
            print(f"Missing {agent_path}")
            continue
            
        print(f"Benchmarking {agent_name}...")
        
        cash_list = []
        wins = 0
        losses = 0
        ties = 0
        
        for opp in opponents:
            for seed in seeds:
                env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
                p1_is_agent1 = (seed % 2 == 0)
                
                try:
                    if p1_is_agent1:
                        env.run([agent_path, opp])
                    else:
                        env.run([opp, agent_path])
                except Exception as e:
                    print(f"Error in game {agent_name} vs {opp}: {e}")
                    continue
                    
                final_step = env.steps[-1]
                if final_step[0].status == "ERROR" or final_step[1].status == "ERROR":
                    continue
                    
                r_a1 = final_step[0].reward or 0
                r_a2 = final_step[1].reward or 0
                
                if p1_is_agent1:
                    my_reward, opp_reward = r_a1, r_a2
                else:
                    my_reward, opp_reward = r_a2, r_a1
                    
                cash_list.append(my_reward)
                if my_reward > opp_reward: wins += 1
                elif my_reward < opp_reward: losses += 1
                else: ties += 1
                
        if len(cash_list) > 0:
            avg_cash = np.mean(cash_list)
            print(f"{agent_name} -> W/L/T: {wins}/{losses}/{ties}, Avg Cash: {avg_cash:.1f}")
            results[agent_name] = {
                'wins': wins, 'losses': losses, 'ties': ties, 'avg_cash': avg_cash
            }

if __name__ == '__main__':
    run_benchmarks()
