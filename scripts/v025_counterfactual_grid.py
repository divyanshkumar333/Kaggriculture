"""
Phase 3 & 4: Capital Allocation Counterfactual Grid & Replay Envelope
=====================================================================
Evaluates the economic feasibility and expected Day-30 contribution of:
- Cow fleet acceleration (D5..D10)
- Strawberry planting timing (D1..D10)
- Worker labor scaling (D0..D10)
- Land expansion timing (Q2, Q3)
"""

import math
import pandas as pd

def evaluate_asset_economics():
    """
    Computes life-cycle metrics for each asset class:
    - Investment cost
    - Days to first revenue
    - Daily revenue
    - Daily operating cost (feed/watering/labor)
    - Net daily margin
    - Payback period
    - Expected Day-30 liquidation value
    """
    days_in_season = 30
    
    # 1. COW purchased on day d
    cow_data = []
    for d in range(4, 16):
        cost = 1500 + 0 # Structure built by labor
        active_days = max(0, 30 - d - 1)
        # Yields 1 Milk every day if fed wheat (feed cost ~$50/day or grown wheat ~$10/day)
        # Milk price: ~$150-180
        daily_rev = 160
        daily_feed = 40 # Average wheat cost
        net_daily = daily_rev - daily_feed
        payback = cost / net_daily if net_daily > 0 else 999
        total_contribution = active_days * net_daily - cost
        cow_data.append({
            "asset": "COW",
            "purchase_day": d,
            "cost": cost,
            "active_days": active_days,
            "daily_margin": net_daily,
            "payback_days": round(payback, 1),
            "expected_net_contrib": total_contribution
        })
        
    # 2. STRAWBERRY planted on day d
    straw_data = []
    for d in range(1, 20):
        cost = 20 # seed cost
        active_days = max(0, 30 - d - 4) # 4 days to first yield
        # Yields 1 strawberry every 2 days (or daily if fertilized/watered)
        # Base price ~$75-90
        # Yields up to 16 days cumulative lifetime
        prod_days = min(active_days, 16)
        daily_rev = 75 * 0.75 # ~0.75 yield/day
        watering_cost = 2
        net_daily = daily_rev - watering_cost
        total_contrib = prod_days * net_daily - cost
        straw_data.append({
            "asset": "STRAWBERRY",
            "planted_day": d,
            "cost": cost,
            "production_days": prod_days,
            "daily_margin": round(net_daily, 1),
            "payback_days": round(cost / net_daily, 1) if net_daily > 0 else 999,
            "expected_net_contrib": round(total_contrib, 1)
        })
        
    df_cow = pd.DataFrame(cow_data)
    df_straw = pd.DataFrame(straw_data)
    
    print("=" * 90)
    print("COW LIFETIME ROI BY PURCHASE DAY")
    print("=" * 90)
    print(df_cow.to_string(index=False))
    
    print("\n" + "=" * 90)
    print("STRAWBERRY LIFETIME ROI BY PLANTING DAY")
    print("=" * 90)
    print(df_straw.head(10).to_string(index=False))
    
    return df_cow, df_straw

if __name__ == "__main__":
    evaluate_asset_economics()
