"""
Phase 7: Replay Gap Checkpoint Comparison
=========================================
Compares Episode 103388734 ($162,805) vs V023-G (and succession candidates) at:
D0, D3, D5, D6, D8, D10, D12, D15, D18, D21, D24, D27, D29, D30
"""

import json
import importlib.util
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

def analyze_replay_vs_agent(agent_path, agent_name="V023-G", seed=42):
    agent_func = load_agent(agent_path)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([agent_func, "random"])
    agent_steps = env.steps
    
    with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
        top_data = json.load(f)
    top_steps = top_data["steps"]
    
    checkpoints = [0, 3, 5, 6, 8, 10, 12, 15, 18, 21, 24, 27, 29, 30]
    
    results = []
    print("=" * 135)
    print(f"CHECKPOINT COMPARISON: Episode 103388734 ($162.8K) vs {agent_name} (Seed {seed})")
    print("=" * 135)
    print(f"{'DAY':<4} | {'TOP BANK':<10} | {'CAND BANK':<10} | {'GAP':<10} | {'TOP C/S/W/SH/WK/QD':<22} | {'CAND C/S/W/SH/WK/QD':<22} | {'KEY DIVERGENCE'}")
    print("-" * 135)
    
    for d in checkpoints:
        if d == 30:
            top_s = len(top_steps) - 1
            ag_s = len(agent_steps) - 1
        else:
            top_s = min(d * 24 + 23, len(top_steps) - 1)
            ag_s = min(d * 24 + 23, len(agent_steps) - 1)
            
        top_obs = top_steps[top_s][1]["observation"]
        ag_obs = agent_steps[ag_s][0]["observation"]
        
        t_stat = extract_stats(top_obs["farms"][1])
        a_stat = extract_stats(ag_obs["farms"][0])
        
        gap = int(round(t_stat["money"] - a_stat["money"]))
        t_money = int(round(t_stat["money"]))
        a_money = int(round(a_stat["money"]))
        
        t_str = f"{t_stat['cows']}c/{t_stat['straw']}s/{t_stat['wheat']}w/{t_stat['sheep']}sh/{t_stat['workers']}wk/{t_stat['quadrants']}q"
        a_str = f"{a_stat['cows']}c/{a_stat['straw']}s/{a_stat['wheat']}w/{a_stat['sheep']}sh/{a_stat['workers']}wk/{a_stat['quadrants']}q"
        
        divergence = ""
        if d == 0:
            divergence = "Identical start ($3000, 1 worker, 1 quad)"
        elif d <= 5:
            divergence = f"Early sheep/cows: Top {t_stat['sheep']}sh/{t_stat['cows']}c vs Cand {a_stat['sheep']}sh/{a_stat['cows']}c"
        elif d <= 10:
            divergence = f"Cow fleet: Top {t_stat['cows']} cows vs Cand {a_stat['cows']} cows; Strawberries {t_stat['straw']} vs {a_stat['straw']}"
        elif d <= 15:
            divergence = f"Strawberry scaling: Top {t_stat['straw']} bushes vs Cand {a_stat['straw']} bushes"
        elif d <= 21:
            divergence = f"Peak Strawberries before decay: Top {t_stat['straw']} vs Cand {a_stat['straw']}"
        elif d <= 27:
            divergence = f"Succession in progress: Top {t_stat['wheat']} wheat ({t_stat['straw']} left) vs Cand {a_stat['wheat']} wheat ({a_stat['straw']} left)"
        else:
            divergence = f"Final liquidation: Top ${t_money:,} vs Cand ${a_money:,}"
            
        print(f"D{d:<3} | ${t_money:<9,d} | ${a_money:<9,d} | ${gap:<9,d} | {t_str:<22} | {a_str:<22} | {divergence}")
        
        results.append({
            "day": d,
            "top_bank": t_stat["money"],
            "cand_bank": a_stat["money"],
            "gap": gap,
            "top_stats": t_stat,
            "cand_stats": a_stat,
            "divergence": divergence,
        })
        
    return results

if __name__ == "__main__":
    analyze_replay_vs_agent("agents/v023_g_capital_optimizer.py", "V023-G (Champion)")
