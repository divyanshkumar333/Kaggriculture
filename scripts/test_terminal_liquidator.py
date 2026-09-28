import os
import sys
import copy
sys.path.insert(0, os.path.abspath("."))
from kaggle_environments import make
from scripts.tournament_population import load_agent

def wrap_with_terminal_liquidator(base_agent_func):
    def gated_agent(obs, config=None):
        action = base_agent_func(obs, config)
        if not isinstance(action, dict):
            return action
            
        day = obs.get('day', int(obs.get('step', 0)) // 24)
        
        if day >= 28: # Typical endgame starts around day 28 out of 30
            market_orders = action.get('market', [])
            new_market = []
            
            # Keep BUY_PRODUCT (e.g. wheat for animals) and HIRE
            for o in market_orders:
                if not isinstance(o, list): o = list(o)
                if len(o) > 0 and o[0] in ('BUY_PRODUCT', 'HIRE'):
                    new_market.append(o)
            
            player = int(obs['player'])
            animal_count = 0
            tiles = obs['farms'][player]['tiles']
            for r in range(len(tiles)):
                for c in range(len(tiles[r])):
                    tile = tiles[r][c]
                    if isinstance(tile, dict) and tile.get('kind') in ('COOP', 'PASTURE') and 'animal' in tile:
                        animal_count += 1
                        
            # Need enough wheat to feed animals for the rest of the game
            remaining_days = max(0, 30 - day)
            wheat_to_keep = animal_count * remaining_days
            
            shed = obs['private']['shed']
            market_prices = obs.get("market", {}).get("prices", {})
            
            sell_candidates = []
            for prod, count in shed.items():
                if count <= 0: continue
                
                sell_amt = count
                if prod == 'WHEAT':
                    sell_amt = max(0, count - wheat_to_keep)
                    
                if sell_amt > 0:
                    price = market_prices.get(prod, 0)
                    # We prioritize by highest value per slot
                    sell_candidates.append((price * sell_amt, prod, sell_amt))
                    
            sell_candidates.sort(reverse=True)
            
            for total_val, prod, count in sell_candidates:
                if len(new_market) >= 10: break
                new_market.append(["SELL", prod, count])
                
            action['market'] = new_market[:10]
            
        return action
        
    return gated_agent

if __name__ == "__main__":
    base_code_path = r"agents\the_2945_farm.py"
    base_agent = load_agent(base_code_path)
    gated_agent = wrap_with_terminal_liquidator(base_agent)
    
    seeds = [42, 101, 2024, 777, 9999, 1234, 5678, 9876, 1111, 2222]
    print(f"Testing Terminal Liquidator Layer vs Base 2945 across {len(seeds)*2} matches...")
    
    wins = 0
    losses = 0
    draws = 0
    margins = []
    
    for s in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([gated_agent, base_agent])
        last = env.steps[-1]
        m0 = last[0]["reward"] - last[1]["reward"]
        margins.append(m0)
        if m0 > 0: wins += 1
        elif m0 < 0: losses += 1
        else: draws += 1
        print(f"Seed {s:5d} | P0: {last[0]['reward']:7.0f} vs {last[1]['reward']:7.0f} | Margin: {m0:+7.0f}")
        
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([base_agent, gated_agent])
        last = env.steps[-1]
        m1 = last[1]["reward"] - last[0]["reward"]
        margins.append(m1)
        if m1 > 0: wins += 1
        elif m1 < 0: losses += 1
        else: draws += 1
        print(f"Seed {s:5d} | P1: {last[1]['reward']:7.0f} vs {last[0]['reward']:7.0f} | Margin: {m1:+7.0f}")
        
    print("=" * 60)
    wr = (wins / len(margins)) * 100
    avg_m = sum(margins) / len(margins)
    print(f"RESULT: {wins}W - {losses}L - {draws}D ({wr:.1f}%) | Mean Margin: {avg_m:+7.0f}")
