import os
import sys
import json
import numpy as np
from datetime import datetime
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
            
        # Extract market state from final step
        obs = final[0].observation
        market_inv = obs.get("market", {}).get("inventory", {})
        market_prices = obs.get("market", {}).get("prices", {})
        
        # Count remaining crops/weeds on agent's farm
        farms = obs.get("farms", [])
        agent_farm = farms[agent_idx] if len(farms) > agent_idx else {}
        opp_farm = farms[opp_idx] if len(farms) > opp_idx else {}
        
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
    
    # Position bias
    p0_results = [r for r in valid if r["agent_pos"] == 0]
    p1_results = [r for r in valid if r["agent_pos"] == 1]
    
    p0_wins = sum(1 for r in p0_results if r["outcome"] == "WIN")
    p1_wins = sum(1 for r in p1_results if r["outcome"] == "WIN")
    
    melon_prices = [r["market_prices"].get("MELON", 0) for r in valid if "market_prices" in r]
    
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
        "p0_win_rate": (p0_wins / len(p0_results) * 100.0) if p0_results else 0,
        "p1_win_rate": (p1_wins / len(p1_results) * 100.0) if p1_results else 0,
        "melon_price_final_mean": float(np.mean(melon_prices)) if melon_prices else 0,
        "agent_weeds_mean": float(np.mean([r["agent_weeds"] for r in valid])),
        "unharvested_yield_mean": float(np.mean([r["agent_unharvested_yield"] for r in valid]))
    }

def run_competitive_benchmark(agent_path="agents/v018_b_batch_cap.py", agent_name="V018-B Control", num_seeds=10):
    seeds = [100 + i for i in range(num_seeds)]
    opponents = [
        ("Self-Play (V018-B)", "agents/v018_b_batch_cap.py"),
        ("Melon Maxxer", "agents/melon_maxxer.py"),
        ("Diversified (V004-B)", "agents/v004_b_diversify.py"),
        ("Animal Multi-Niche (V005-C)", "agents/v005_c_best_animal.py"),
        ("Starter", "starter"),
        ("Random", "random"),
    ]
    
    print(f"==================================================")
    print(f"RUNNING COMPETITIVE BENCHMARK FOR {agent_name}")
    print(f"Seeds: {len(seeds)} | Total Games: {len(seeds) * len(opponents)}")
    print(f"==================================================")
    
    summary = []
    for opp_name, opp_path in opponents:
        print(f"Testing vs {opp_name}...")
        report = evaluate_matchup(agent_name, agent_path, opp_name, opp_path, seeds)
        summary.append(report)
        print(f"  -> Win Rate: {report['win_rate']:.1f}% | Agent Bank: ${report['agent_bank_mean']:.0f} | Opp Bank: ${report['opp_bank_mean']:.0f} | Delta: ${report['delta_mean']:+.0f} | Final Melon Price: ${report['melon_price_final_mean']:.1f}")
        
    print(f"\n==================================================")
    print(f"BENCHMARK SUMMARY FOR {agent_name}")
    print(f"==================================================")
    
    total_wins = sum(s["wins"] for s in summary)
    total_games = sum(s["total_games"] for s in summary)
    overall_win_rate = (total_wins / total_games) * 100.0
    overall_mean_bank = np.mean([s["agent_bank_mean"] for s in summary])
    
    print(f"Overall Win Rate: {overall_win_rate:.1f}% ({total_wins}/{total_games})")
    print(f"Overall Mean Bank: ${overall_mean_bank:.0f}")
    
    # Save results to json
    os.makedirs("experiments", exist_ok=True)
    with open("experiments/competitive_benchmark_v018_b.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved to experiments/competitive_benchmark_v018_b.json")
    return summary

if __name__ == "__main__":
    run_competitive_benchmark(num_seeds=10)
