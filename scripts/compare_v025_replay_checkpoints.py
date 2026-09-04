"""
Phase 9: V025 Replay Gap Checkpoint Evaluation
==============================================
Compares Episode 103388734 ($162,805) vs V023-G and V025 candidates at:
D0, D3, D5, D6, D8, D10, D12, D15, D18, D21, D24, D27, D29, D30
"""

import json
import importlib.util
import pandas as pd
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

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
    return {
        "money": farm["money"],
        "cows": cows,
        "sheep": sheep,
        "straw": straw,
        "wheat": wheat,
        "melons": melons,
        "carrots": carrots,
        "workers": 1 + len(farm["hands"]),
        "quadrants": len(farm["unlocked_quadrants"]),
    }

def analyze_checkpoints(candidates, seed=42):
    with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
        top_data = json.load(f)
    top_steps = top_data["steps"]
    
    checkpoints = [0, 3, 5, 6, 8, 10, 12, 15, 18, 21, 24, 27, 29, 30]
    
    agent_traces = {}
    for cname, cpath in candidates:
        agent_func = load_agent(cpath)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([agent_func, "random"])
        agent_traces[cname] = env.steps
        
    print("=" * 135)
    print(f"14-CHECKPOINT COMPARISON: TOP REPLAY ($162.8K) VS V023-G & V025 CANDIDATES (Seed {seed})")
    print("=" * 135)
    
    rows = []
    for d in checkpoints:
        if d == 30:
            top_s = len(top_steps) - 1
        else:
            top_s = min(d * 24 + 23, len(top_steps) - 1)
            
        top_obs = top_steps[top_s][1]["observation"]
        t_stat = extract_stats(top_obs["farms"][1])
        t_money = int(round(t_stat["money"]))
        
        row_dict = {
            "DAY": f"D{d}",
            "TOP_REPLAY": f"${t_money:,} ({t_stat['cows']}c/{t_stat['straw']}s/{t_stat['workers']}w)"
        }
        
        for cname, cpath in candidates:
            steps = agent_traces[cname]
            ag_s = len(steps) - 1 if d == 30 else min(d * 24 + 23, len(steps) - 1)
            ag_obs = steps[ag_s][0]["observation"]
            a_stat = extract_stats(ag_obs["farms"][0])
            a_money = int(round(a_stat["money"]))
            row_dict[cname] = f"${a_money:,} ({a_stat['cows']}c/{a_stat['straw']}s/{a_stat['workers']}w)"
            
        rows.append(row_dict)
        
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    return df

if __name__ == "__main__":
    candidates = [
        ("V023-G", "agents/v023_g_capital_optimizer.py"),
        ("V025-A", "agents/v025_a_aggressive_cows.py"),
        ("V025-B", "agents/v025_b_balanced_ramp.py"),
        ("V025-E", "agents/v025_e_hybrid_flywheel.py"),
    ]
    analyze_checkpoints(candidates, seed=42)
