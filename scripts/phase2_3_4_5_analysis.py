"""
Phase 2, 3, 4, 5: Flywheel Trajectory, Capital Allocation Frontier, Replay Dive, and Bottlenecks
"""

import importlib.util
import json
import numpy as np
from kaggle_environments import make

# -----------------------------------------------------------------------------
# PHASE 2: COW TRAJECTORY EXPERIMENT
# -----------------------------------------------------------------------------
print("="*80)
print("PHASE 2: CONTROLLED COW PURCHASE TRAJECTORY EXPERIMENT (Seeds 1000..1019)")
print("="*80)

# We test 4 explicit Day-6 cow purchase limits: 1, 2, 3, 4 cows
cow_variants = {}
for max_cows_d6 in [1, 2, 3, 4]:
    # Modify v023_e dynamically
    with open("agents/v023_e_cows_first_flywheel.py", "r") as f:
        code = f.read()
    
    # Replace cow purchase logic
    old_logic = 'n_cows_to_buy = 2 if money >= 3200 else (1 if money >= 1500 else 0)'
    if max_cows_d6 == 1:
        new_logic = 'n_cows_to_buy = 1 if money >= 1500 else 0'
    elif max_cows_d6 == 2:
        new_logic = 'n_cows_to_buy = 2 if money >= 3200 else (1 if money >= 1500 else 0)'
    elif max_cows_d6 == 3:
        new_logic = 'n_cows_to_buy = 3 if money >= 4700 else (2 if money >= 3200 else (1 if money >= 1500 else 0))'
    elif max_cows_d6 == 4:
        new_logic = 'n_cows_to_buy = 4 if money >= 6200 else (3 if money >= 4700 else (2 if money >= 3200 else (1 if money >= 1500 else 0)))'
        
    v_code = code.replace(old_logic, new_logic)
    v_path = f"scratch/v023_cow_v{max_cows_d6}.py"
    with open(v_path, "w") as f:
        f.write(v_code)
        
    spec = importlib.util.spec_from_file_location(f"v_{max_cows_d6}", v_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    scores = []
    for s in range(1000, 1020):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([mod.agent, "random"])
        scores.append(env.steps[-1][0]["reward"])
        
    mean_s = np.mean(scores)
    med_s = np.median(scores)
    min_s = np.min(scores)
    max_s = np.max(scores)
    print(f"Variant {max_cows_d6} Cows/Turn: Mean: ${mean_s:7,.0f} | Median: ${med_s:7,.0f} | Min: ${min_s:7,.0f} | Max: ${max_s:7,.0f}")
    cow_variants[f"max_{max_cows_d6}"] = {"mean": float(mean_s), "median": float(med_s), "min": float(min_s), "max": float(max_s)}

# -----------------------------------------------------------------------------
# PHASE 3: CAPITAL ALLOCATION FRONTIER TABLE
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("PHASE 3: CAPITAL ALLOCATION FRONTIER (POST-DAY 6 LIQUIDITY)")
print("="*80)
frontier = [
    {"Resource": "Cow (+Pasture)", "Cost": 1600, "LeadTime": 2, "DailyRev": 450, "PaybackDays": 3.55, "Profit30D": 8300, "CapitalEfficiency": "High (Liquidity generator)"},
    {"Resource": "Sheep (+Pasture)", "Cost": 1100, "LeadTime": 6, "DailyRev": 570, "PaybackDays": 1.93, "Profit30D": 10300, "CapitalEfficiency": "Very High (Lumpy 6D cycles)"},
    {"Resource": "Strawberry (x10 seeds)", "Cost": 200, "LeadTime": 5, "DailyRev": 2400, "PaybackDays": 0.08, "Profit30D": 9400, "CapitalEfficiency": "Maximum (Requires water labor)"},
    {"Resource": "Melon (x5 seeds)", "Cost": 400, "LeadTime": 10, "DailyRev": 600, "PaybackDays": 0.67, "Profit30D": 5600, "CapitalEfficiency": "Medium (Long 10D cycle)"},
    {"Resource": "Wheat (x10 seeds)", "Cost": 100, "LeadTime": 2, "DailyRev": 600, "PaybackDays": 0.17, "Profit30D": 1100, "CapitalEfficiency": "Low absolute profit"},
    {"Resource": "Q2 Unlock (25 tiles)", "Cost": 1400, "LeadTime": 0, "DailyRev": 0, "PaybackDays": 1.5, "Profit30D": 20000, "CapitalEfficiency": "Mandatory space enabler"},
    {"Resource": "Q3 Unlock (25 tiles)", "Cost": 2800, "LeadTime": 0, "DailyRev": 0, "PaybackDays": 2.0, "Profit30D": 20000, "CapitalEfficiency": "Mandatory space enabler"},
    {"Resource": "Hired Hand (N=6..10)", "Cost": 54, "LeadTime": 0, "DailyRev": 400, "PaybackDays": 0.14, "Profit30D": 7000, "CapitalEfficiency": "Critical labor enabler"}
]

print(f"{'Resource':<25} | {'Cost':<6} | {'Lead':<4} | {'DailyRev':<8} | {'Payback':<7} | {'30D Profit':<10} | {'Efficiency'}")
print("-"*85)
for f in frontier:
    print(f"{f['Resource']:<25} | ${f['Cost']:<5} | {f['LeadTime']:<4} | ${f['DailyRev']:<7} | {f['PaybackDays']:4.2f}d  | ${f['Profit30D']:<9} | {f['CapitalEfficiency']}")

# -----------------------------------------------------------------------------
# PHASE 4: INVESTIGATE EPISODE 103388734 ($162.8K) DIVERGENCE
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("PHASE 4: EPISODE 103388734 ($162.8K) REPLAY DEEP DIVE")
print("="*80)

with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
    replay_data = json.load(f)

top_p = 1
steps = replay_data["steps"]

replay_timeline = []
for d in range(30):
    s = d * 24 + 23
    obs = steps[s][0]["observation"]
    f = obs["farms"][top_p]
    p_shed = obs["farms"][top_p]["money"]
    cows = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "COW")
    sheep = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("animal") == "SHEEP")
    straws = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("crop") == "STRAWBERRY")
    wheat = sum(1 for row in f["tiles"] for t in row if isinstance(t, dict) and t.get("crop") == "WHEAT")
    
    replay_timeline.append({
        "day": d, "bank": f["money"], "quads": len(f["unlocked_quadrants"]),
        "cows": cows, "sheep": sheep, "straws": straws, "wheat": wheat, "hands": len(f["hands"])
    })
    if d in [0, 5, 6, 7, 8, 9, 10, 12, 15, 18, 21, 24, 27, 29]:
        print(f"Day {d:2d}: Bank=${f['money']:7,.0f} | Quads={len(f['unlocked_quadrants'])} | Cows={cows:2d} | Sheep={sheep:2d} | Straws={straws:2d} | Wheat={wheat:2d} | Hands={len(f['hands']):2d}")

# -----------------------------------------------------------------------------
# PHASE 5: INSTRUMENTATION FOR LOST POTENTIAL REVENUE IN V023-E
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("PHASE 5: INSTRUMENTATION OF LOST REVENUE IN V023-E (Seed 1000)")
print("="*80)

spec = importlib.util.spec_from_file_location("v23e", "agents/v023_e_cows_first_flywheel.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 1000}, debug=False)
env.run([mod.agent, "random"])

lost_rev_report = {
    "idle_cash_peak": 0.0,
    "unsold_milk_end": 0,
    "unsold_wool_end": 0,
    "unsold_straw_end": 0,
    "unsold_fert_end": 0,
    "unwatered_straw_days": 0,
    "cows_unplaced_days": 0
}

final_obs = env.steps[-1][0]["observation"]
final_shed = final_obs["private"]["shed"]
lost_rev_report["unsold_milk_end"] = final_shed.get("MILK", 0)
lost_rev_report["unsold_wool_end"] = final_shed.get("WOOL", 0)
lost_rev_report["unsold_straw_end"] = final_shed.get("STRAWBERRY", 0)
lost_rev_report["unsold_fert_end"] = final_shed.get("FERTILIZER", 0)

print(f"Unsold Warehouse Liquidity at Turn 720:")
print(f"  Unsold Milk: {lost_rev_report['unsold_milk_end']} units (~${lost_rev_report['unsold_milk_end']*180:,.0f} lost cash)")
print(f"  Unsold Wool: {lost_rev_report['unsold_wool_end']} units (~${lost_rev_report['unsold_wool_end']*240:,.0f} lost cash)")
print(f"  Unsold Strawberry: {lost_rev_report['unsold_straw_end']} units (~${lost_rev_report['unsold_straw_end']*120:,.0f} lost cash)")
print(f"  Unsold Fertilizer: {lost_rev_report['unsold_fert_end']} units (~${lost_rev_report['unsold_fert_end']*100:,.0f} lost cash)")

total_lost_inv_cash = (
    lost_rev_report['unsold_milk_end']*180 +
    lost_rev_report['unsold_wool_end']*240 +
    lost_rev_report['unsold_straw_end']*120 +
    lost_rev_report['unsold_fert_end']*100
)
print(f"Total Trapped Liquidity: ${total_lost_inv_cash:,.0f}")

with open("scratch/phase2_5_analysis.json", "w") as f:
    json.dump({
        "cow_variants": cow_variants,
        "frontier": frontier,
        "replay_timeline": replay_timeline,
        "lost_revenue": lost_rev_report
    }, f, indent=2)
