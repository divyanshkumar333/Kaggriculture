import os
import json
import numpy as np
from kaggle_environments import make

def get_stats(replay, player_id):
    steps = replay['steps']
    stats = {'final_cash': 0, 'melon': 0, 'strawberry': 0, 'wheat': 0, 'carrot': 0, 'milk': 0, 'wool': 0, 'egg': 0, 'hires': 0, 'market_orders': 0}
    
    final_state = steps[-1][player_id]['observation']['farms'][player_id]
    stats['final_cash'] = final_state['money']
    
    # We can estimate production by total sells + final shed inventory
    # But let's keep it simple first: just final_cash and hires
    for step in steps:
        action = step[player_id].get('action', {})
        if not isinstance(action, dict): continue
        market = action.get('market', [])
        stats['market_orders'] += len(market)
        for m in market:
            if m and m[0] == 'HIRE':
                stats['hires'] += 1
            if m and m[0] == 'SELL':
                item = m[1].lower()
                qty = m[2]
                if item in stats:
                    stats[item] += qty

    # add final shed inventory to production stats
    shed = steps[-1][player_id]['observation']['private']['shed']
    for k, v in shed.items():
        item = k.lower()
        if item in stats:
            stats[item] += v

    return stats

def run_benchmarks():
    routes = [0, 2, 3, 9, 100, 103, 104, 105, 106, 110, 128] # just sample of distinct routes for speed first
    opponents = ['agents/final_v16_ranked.py', 'agents/014_robust_trace.py', 'agents/v063_meta_router.py']
    seeds = [42, 43]
    
    results = []
    
    for r in routes:
        agent_path = f'agents/forced_routes/v104_route_{r}.py'
        if not os.path.exists(agent_path): continue
        
        route_cash = []
        route_wins = 0
        route_losses = 0
        route_ties = 0
        route_stats = []
        
        print(f"Benchmarking Route {r}...")
        for opp in opponents:
            for seed in seeds:
                env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
                # Swap seats
                p1_is_agent1 = (seed % 2 == 0)
                
                try:
                    if p1_is_agent1:
                        env.run([agent_path, opp])
                    else:
                        env.run([opp, agent_path])
                except Exception as e:
                    print(f"Error in game Route {r} vs {opp}: {e}")
                    continue
                    
                final_step = env.steps[-1]
                if final_step[0].status == "ERROR" or final_step[1].status == "ERROR":
                    continue
                    
                r_a1 = final_step[0].reward or 0
                r_a2 = final_step[1].reward or 0
                
                if p1_is_agent1:
                    my_reward, opp_reward = r_a1, r_a2
                    my_id = 0
                else:
                    my_reward, opp_reward = r_a2, r_a1
                    my_id = 1
                    
                route_cash.append(my_reward)
                if my_reward > opp_reward: route_wins += 1
                elif my_reward < opp_reward: route_losses += 1
                else: route_ties += 1
                
                stats = get_stats(env.toJSON(), my_id)
                route_stats.append(stats)
                
        if len(route_cash) > 0:
            avg_cash = np.mean(route_cash)
            avg_melon = np.mean([s['melon'] for s in route_stats])
            avg_wheat = np.mean([s['wheat'] for s in route_stats])
            avg_hires = np.mean([s['hires'] for s in route_stats])
            print(f"Route {r} -> W/L/T: {route_wins}/{route_losses}/{route_ties}, Avg Cash: {avg_cash:.1f}, Avg Hires: {avg_hires:.1f}, Melon: {avg_melon:.1f}, Wheat: {avg_wheat:.1f}")
            results.append({
                'route': r,
                'wins': route_wins,
                'losses': route_losses,
                'ties': route_ties,
                'avg_cash': avg_cash,
                'avg_hires': avg_hires,
                'avg_melon': avg_melon,
                'avg_wheat': avg_wheat
            })
            
    # Save results
    with open('phase1_route_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    run_benchmarks()
