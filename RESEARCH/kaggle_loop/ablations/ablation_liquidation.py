import os
import sys
sys.path.insert(0, os.path.abspath("."))
import collections
from kaggle_environments import make
from scripts.tournament_population import load_agent

def run_liquidation_ablation(seeds=[42, 101, 2024, 777, 9999]):
    print("=" * 60)
    print("ABLATION: DAY-28 LIQUIDATION & FINAL RESIDUAL ASSETS")
    print("Investigating: unliquidated assets at final step 718 (step 719 scoring)")
    print("=" * 60)
    
    base_agent = load_agent(r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py")
    
    total_unrealized_shed_value = 0
    total_unrealized_carried_value = 0
    total_unrealized_field_value = 0
    
    for seed in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([base_agent, "pass"])
        
        last_step = env.steps[-1][0]["observation"]
        prices = last_step["market"]["prices"]
        shed = last_step["private"]["shed"]
        inventories = last_step["private"]["inventories"]
        farm = last_step["farms"][0]
        tiles = farm["tiles"]
        
        shed_val = sum(count * prices.get(item, 1) for item, count in shed.items() if count > 0 and item in prices)
        carried_val = sum(sum(count * prices.get(item, 1) for item, count in inv.items() if count > 0 and item in prices) for inv in inventories)
        
        field_val = 0
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    y = t.get("yield_units", 0)
                    if y > 0:
                        prod = t.get("crop") or ({"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}.get(t.get("animal")))
                        if prod and prod in prices:
                            field_val += y * prices.get(prod, 1)
                            
        total_unrealized_shed_value += shed_val
        total_unrealized_carried_value += carried_val
        total_unrealized_field_value += field_val
        print(f"Seed {seed}: Final Cash = ${farm['money']:,.0f} | Unsold Shed = ${shed_val:,.0f} | Carried = ${carried_val:,.0f} | Unharvested Field = ${field_val:,.0f}")
        
    n = len(seeds)
    print("-" * 60)
    print(f"Mean Unsold in Shed: ${total_unrealized_shed_value/n:,.0f}")
    print(f"Mean Carried by Workers: ${total_unrealized_carried_value/n:,.0f}")
    print(f"Mean Unharvested in Field: ${total_unrealized_field_value/n:,.0f}")
    print(f"Total Left On The Table: ${(total_unrealized_shed_value + total_unrealized_carried_value + total_unrealized_field_value)/n:,.0f} per game!")
    print("=" * 60)

if __name__ == "__main__":
    run_liquidation_ablation()
