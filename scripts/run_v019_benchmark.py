import os
import sys
import json
import numpy as np
import importlib.util
from kaggle_environments import make

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

def run_single_game(agent_path, opp_path, seed, p1_is_agent):
    os.environ["KAGGRICULTURE_SEED"] = str(seed)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    
    agent1 = load_agent(agent_path)
    agent2 = load_agent(opp_path)
    
    agents = [agent1, agent2] if p1_is_agent else [agent2, agent1]
    
    try:
        env.run(agents)
        final = env.steps[-1]
        
        agent_idx = 0 if p1_is_agent else 1
        opp_idx = 1 if p1_is_agent else 0
        
        agent_bank = float(final[agent_idx].reward or 0)
        opp_bank = float(final[opp_idx].reward or 0)
        
        if agent_bank > opp_bank:
            outcome = "WIN"
        elif agent_bank < opp_bank:
            outcome = "LOSS"
        else:
            outcome = "TIE"
            
        obs = final[0].observation
        market_prices = obs.get("market", {}).get("prices", {})
        
        farms = obs.get("farms", [])
        agent_farm = farms[agent_idx] if len(farms) > agent_idx else {}
        
        agent_tiles = agent_farm.get("tiles", [])
        agent_weeds = 0
        agent_plants = 0
        agent_unharvested_yield = 0
        for row in agent_tiles:
            for tile in row:
                if isinstance(tile, dict):
                    if tile.get("kind") == "WEED":
                        agent_weeds += 1
                    elif tile.get("kind") == "PLANT":
                        agent_plants += 1
                        agent_unharvested_yield += tile.get("yield_units", 0)
                        
        return {
            "status": "SUCCESS",
            "seed": seed,
            "agent_pos": agent_idx,
            "agent_bank": agent_bank,
            "opp_bank": opp_bank,
            "delta": agent_bank - opp_bank,
            "outcome": outcome,
            "market_prices": market_prices,
            "agent_weeds": agent_weeds,
            "agent_plants_left": agent_plants,
            "agent_unharvested_yield": agent_unharvested_yield
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "seed": seed,
            "agent_bank": 0,
            "opp_bank": 0,
            "delta": 0,
            "outcome": "ERROR"
        }

def evaluate_matchup(agent_name, agent_path, opp_name, opp_path, seeds):
    results = []
    for i, seed in enumerate(seeds):
        p1_is_agent = (i % 2 == 0)
        res = run_single_game(agent_path, opp_path, seed, p1_is_agent)
        results.append(res)
        
    valid = [r for r in results if r["status"] == "SUCCESS"]
    if not valid:
        return {"agent": agent_name, "opp": opp_name, "error": "No successful games"}
        
    agent_banks = [r["agent_bank"] for r in valid]
    opp_banks = [r["opp_bank"] for r in valid]
    deltas = [r["delta"] for r in valid]
    wins = sum(1 for r in valid if r["outcome"] == "WIN")
    losses = sum(1 for r in valid if r["outcome"] == "LOSS")
    ties = sum(1 for r in valid if r["outcome"] == "TIE")
    total = len(valid)
    
    melon_prices = [r["market_prices"].get("MELON", 0) for r in valid if "market_prices" in r]
    carrot_prices = [r["market_prices"].get("CARROT", 0) for r in valid if "market_prices" in r]
    
    return {
        "agent": agent_name,
        "opp": opp_name,
        "total_games": total,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": (wins / total) * 100.0,
        "agent_bank_mean": float(np.mean(agent_banks)),
        "agent_bank_median": float(np.median(agent_banks)),
        "agent_bank_std": float(np.std(agent_banks)),
        "agent_bank_min": float(np.min(agent_banks)),
        "agent_bank_max": float(np.max(agent_banks)),
        "opp_bank_mean": float(np.mean(opp_banks)),
        "delta_mean": float(np.mean(deltas)),
        "delta_median": float(np.median(deltas)),
        "melon_price_final_mean": float(np.mean(melon_prices)) if melon_prices else 0,
        "carrot_price_final_mean": float(np.mean(carrot_prices)) if carrot_prices else 0,
        "agent_weeds_mean": float(np.mean([r["agent_weeds"] for r in valid])),
        "unharvested_yield_mean": float(np.mean([r["agent_unharvested_yield"] for r in valid]))
    }

def run_head_to_head(agent_a_path, agent_b_path, seeds):
    print(f"\n==================================================")
    print(f"DIRECT HEAD-TO-HEAD: V019-B vs V019-A (Control)")
    print(f"Seeds: {len(seeds)} (Alternating Positions)")
    print(f"==================================================")
    report = evaluate_matchup("V019-B Market Adaptive", agent_b_path, "V019-A Control", agent_a_path, seeds)
    print(f"V019-B Win Rate vs V019-A: {report['win_rate']:.1f}% ({report['wins']}W / {report['losses']}L / {report['ties']}T)")
    print(f"V019-B Mean Bank: ${report['agent_bank_mean']:.0f} (Min: ${report['agent_bank_min']:.0f}, Max: ${report['agent_bank_max']:.0f})")
    print(f"V019-A Mean Bank: ${report['opp_bank_mean']:.0f}")
    print(f"Bank Delta (B - A): ${report['delta_mean']:+.0f}")
    return report

def main():
    num_seeds = 12
    seeds = [200 + i for i in range(num_seeds)]
    
    agent_a_path = "agents/v019_a_control.py"
    agent_b_path = "agents/v019_b_market_adaptive.py"
    
    # 1. Direct Head-to-Head
    h2h_report = run_head_to_head(agent_a_path, agent_b_path, seeds)
    
    # 2. Field Benchmark
    opponents = [
        ("Diversified (V004-B)", "agents/v004_b_diversify.py"),
        ("Animal Optimizer (V005-D)", "agents/v005_d_combined.py"),
        ("Melon Maxxer", "agents/melon_maxxer.py"),
        ("Starter", "starter"),
        ("Random", "random"),
    ]
    
    print(f"\n==================================================")
    print(f"FIELD BENCHMARK: V019-A (Control) vs FIELD")
    print(f"==================================================")
    summary_a = [h2h_report]
    for opp_name, opp_path in opponents:
        rep = evaluate_matchup("V019-A Control", agent_a_path, opp_name, opp_path, seeds)
        summary_a.append(rep)
        print(f"vs {opp_name:25s} | Win: {rep['win_rate']:5.1f}% | Bank: ${rep['agent_bank_mean']:6.0f} | Opp: ${rep['opp_bank_mean']:6.0f} | Delta: ${rep['delta_mean']:+6.0f}")
        
    print(f"\n==================================================")
    print(f"FIELD BENCHMARK: V019-B (Market Adaptive) vs FIELD")
    print(f"==================================================")
    summary_b = [h2h_report]
    for opp_name, opp_path in opponents:
        rep = evaluate_matchup("V019-B Market Adaptive", agent_b_path, opp_name, opp_path, seeds)
        summary_b.append(rep)
        print(f"vs {opp_name:25s} | Win: {rep['win_rate']:5.1f}% | Bank: ${rep['agent_bank_mean']:6.0f} | Opp: ${rep['opp_bank_mean']:6.0f} | Delta: ${rep['delta_mean']:+6.0f}")
        
    # Overall summary
    total_wins_a = sum(s["wins"] for s in summary_a[1:]) # exclude h2h for clean field comparison
    total_games_a = sum(s["total_games"] for s in summary_a[1:])
    total_wins_b = sum(s["wins"] for s in summary_b[1:])
    total_games_b = sum(s["total_games"] for s in summary_b[1:])
    
    print(f"\n==================================================")
    print(f"OVERALL RESULTS SUMMARY")
    print(f"==================================================")
    print(f"Head-to-Head: V019-B vs V019-A -> Win Rate: {h2h_report['win_rate']:.1f}% ({h2h_report['wins']}W / {h2h_report['losses']}L / {h2h_report['ties']}T)")
    print(f"V019-A Control Field Win Rate:   {(total_wins_a/total_games_a)*100:.1f}% | Mean Bank: ${np.mean([s['agent_bank_mean'] for s in summary_a[1:]]):.0f} | Worst Case: ${np.min([s['agent_bank_min'] for s in summary_a[1:]]):.0f}")
    print(f"V019-B Adaptive Field Win Rate:  {(total_wins_b/total_games_b)*100:.1f}% | Mean Bank: ${np.mean([s['agent_bank_mean'] for s in summary_b[1:]]):.0f} | Worst Case: ${np.min([s['agent_bank_min'] for s in summary_b[1:]]):.0f}")
    
    results = {
        "head_to_head": h2h_report,
        "v019_a_field": summary_a,
        "v019_b_field": summary_b
    }
    
    os.makedirs("experiments", exist_ok=True)
    with open("experiments/v019_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved complete results to experiments/v019_benchmark_results.json")

if __name__ == "__main__":
    main()
