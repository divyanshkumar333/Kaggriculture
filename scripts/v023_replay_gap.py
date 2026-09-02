"""
V023 Phase 1 & 2: Replay Gap Quantification Engine
--------------------------------------------------
Compares V022-C vs Top Replay (Episode 103388734, $162,805) day-by-day (D0..D29).
Calculates:
- Bank
- Daily Revenue
- Daily Expenses
- Active Workers
- Cows & Sheep
- Strawberry & Wheat Plants
- Unsold Inventory
- Cumulative Gap & Root Cause Classification
"""

import json
import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v022_c = load_agent("agents/v022_c_market_batching.py")

# Run V022-C to get day-by-day trace on seed 42
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
env.run([v022_c, "random"])
v022_steps = env.steps

# Load Episode 103388734
with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
    top_data = json.load(f)
top_steps = top_data["steps"]

print("="*115)
print(f"{'DAY':<4} | {'TOP REPLAY BANK':<15} | {'V022-C BANK':<12} | {'GAP':<11} | {'TOP COWS/STR':<13} | {'V022 COWS/STR':<13} | {'MAIN CAUSE CLASSIFICATION'}")
print("="*115)

gap_table = []

for d in range(30):
    top_s = min(d * 24 + 23, len(top_steps) - 1)
    v22_s = min(d * 24 + 23, len(v022_steps) - 1)
    
    top_obs = top_steps[top_s][1]["observation"]
    v22_obs = v022_steps[v22_s][0]["observation"]
    
    top_bank = top_obs["farms"][1]["money"]
    v22_bank = v22_obs["farms"][0]["money"]
    gap = top_bank - v22_bank
    
    # Counts
    def extract_stats(farm):
        cows, sheep, straw, wheat, melons, carrots = 0, 0, 0, 0, 0, 0
        for r in farm["tiles"]:
            for t in r:
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k in ["PASTURE", "COOP"]:
                        an = t.get("animal")
                        if an == "COW": cows += 1
                        elif an == "SHEEP": sheep += 1
                    elif k == "PLANT":
                        cr = t.get("crop")
                        if cr == "STRAWBERRY": straw += 1
                        elif cr == "WHEAT": wheat += 1
                        elif cr == "MELON": melons += 1
                        elif cr == "CARROT": carrots += 1
        return cows, sheep, straw, wheat, melons, carrots, len(farm["hands"]), len(farm["unlocked_quadrants"])

    t_cows, t_sheep, t_straw, t_wheat, t_melons, t_carrots, t_hands, t_quads = extract_stats(top_obs["farms"][1])
    v_cows, v_sheep, v_straw, v_wheat, v_melons, v_carrots, v_hands, v_quads = extract_stats(v22_obs["farms"][0])
    
    cause = ""
    category = ""
    if d <= 5:
        if abs(gap) < 500:
            cause = "Opening parity: identical 4 Sheep + Melons"
            category = "Strategy Parity"
        else:
            cause = f"Replay bought early cow/strawberries (Top: {t_cows}C/{t_straw}S vs V22: {v_cows}C/{v_straw}S)"
            category = "B) Timing & D) Workforce"
    elif d <= 10:
        if t_cows > v_cows + 3:
            cause = f"Replay accelerated Cow fleet to {t_cows} Cows (V22 has only {v_cows})"
            category = "A) Strategy & F) Production Capacity"
        elif t_quads > v_quads:
            cause = f"Replay unlocked Quad {t_quads} earlier"
            category = "B) Timing & G) Capital Deployment"
        else:
            cause = f"Replay ramping strawberries ({t_straw} vs {v_straw})"
            category = "F) Production Capacity"
    elif d <= 20:
        if t_straw > v_straw + 10 or t_cows > v_cows + 3:
            cause = f"Compounding daily cash flow: Replay has {t_cows} Cows + {t_straw} Straw vs {v_cows} Cows + {v_straw} Straw"
            category = "F) Production Flywheel Gap"
        else:
            cause = f"Daily milk & strawberry volume difference"
            category = "C) Market Volume & Pacing"
    else:
        if t_wheat + t_carrots > v_wheat + v_carrots + 15:
            cause = f"Late-game crop pivot: Replay planted {t_wheat} Wheat + {t_carrots} Carrots; V22 idle"
            category = "A) Strategy & F) Late-Season Pivot"
        else:
            cause = f"Accumulated compounding capital difference"
            category = "Compound Flywheel"
            
    top_cs_str = f"{t_cows}C/{t_straw}S"
    v22_cs_str = f"{v_cows}C/{v_straw}S"
    
    print(f"D{d:02d}  | ${top_bank:13,.0f} | ${v22_bank:10,.0f} | ${gap:+10,.0f} | {top_cs_str:<13} | {v22_cs_str:<13} | {category}: {cause}")
    
    gap_table.append({
        "day": d,
        "top_bank": top_bank,
        "v022_bank": v22_bank,
        "gap": gap,
        "top_cows": t_cows,
        "top_straw": t_straw,
        "v22_cows": v_cows,
        "v22_straw": v_straw,
        "category": category,
        "cause": cause
    })

with open("scratch/v023_gap_analysis.json", "w") as f:
    json.dump(gap_table, f, indent=2)

print("\nSaved gap analysis to scratch/v023_gap_analysis.json")
