"""
V023 Capital Optimizer Standalone Tool
---------------------------------------
Computes marginal ROI rankings, payback horizons, and capital allocation frontiers
for Kaggriculture game economy across any day D (0..30).
"""

import math

def calculate_frontier(current_day, bank, unlocked_quads, num_animals, num_strawberries):
    days_left = max(0, 30 - current_day)
    
    # Costs
    cost_cow = 1600 # Cow ($1500) + Pasture ($100)
    cost_sheep = 1100 # Sheep ($1000) + Pasture ($100)
    cost_straw = 25 # Seed ($20) + Labor amortized ($5)
    cost_melon = 85
    cost_wheat = 10
    cost_q2 = 1400
    cost_q3 = 2800
    cost_q4 = 7000
    
    # Expected Lifetime Margins
    cow_yield_days = max(0, days_left - 2)
    cow_daily_rev = 450 # 2 Milk ($360) + 1 Fert ($100) - 1 Feed ($10)
    cow_lifetime_profit = (cow_yield_days * cow_daily_rev) - cost_cow
    cow_roi = (cow_lifetime_profit / cost_cow) if cow_yield_days > 0 else -1.0
    
    sheep_cycles = max(0, days_left - 6) // 6
    sheep_lifetime_profit = (sheep_cycles * 3420) - cost_sheep
    sheep_roi = (sheep_lifetime_profit / cost_sheep) if sheep_cycles > 0 else -1.0
    
    straw_yield_days = min(max(0, days_left - 5), 8)
    straw_lifetime_profit = (straw_yield_days * 120) - cost_straw
    straw_roi = (straw_lifetime_profit / cost_straw) if straw_yield_days > 0 else -1.0
    
    wheat_cycles = max(0, days_left - 2) // 2
    wheat_lifetime_profit = (wheat_cycles * 110) - cost_wheat
    wheat_roi = (wheat_lifetime_profit / cost_wheat) if wheat_cycles > 0 else -1.0
    
    investments = [
        {"Resource": "COW", "Cost": cost_cow, "DailyNet": cow_daily_rev, "PaybackDays": 3.55, "LifetimeProfit": cow_lifetime_profit, "ROI": cow_roi},
        {"Resource": "SHEEP", "Cost": cost_sheep, "DailyNet": 570, "PaybackDays": 1.93, "LifetimeProfit": sheep_lifetime_profit, "ROI": sheep_roi},
        {"Resource": "STRAWBERRY", "Cost": cost_straw, "DailyNet": 120, "PaybackDays": 0.21, "LifetimeProfit": straw_lifetime_profit, "ROI": straw_roi},
        {"Resource": "WHEAT", "Cost": cost_wheat, "DailyNet": 55, "PaybackDays": 0.18, "LifetimeProfit": wheat_lifetime_profit, "ROI": wheat_roi},
    ]
    
    # Sort by expected lifetime profit & ROI
    investments.sort(key=lambda x: x["LifetimeProfit"], reverse=True)
    return investments

if __name__ == "__main__":
    print("="*80)
    print("KAGGRICULTURE CAPITAL ALLOCATION OPTIMIZER: LIFETIME ROI ACROSS SEASON")
    print("="*80)
    for d in [0, 6, 10, 15, 20, 24, 27]:
        print(f"\n--- DAY {d} (Days Left: {30-d}) ---")
        frontier = calculate_frontier(d, 5000, ["NW", "NE"], 8, 20)
        for item in frontier:
            print(f"  {item['Resource']:<12}: Profit=${item['LifetimeProfit']:>6,.0f} | ROI: {item['ROI']:>6.2f}x | Payback: {item['PaybackDays']:>4.2f}d")
