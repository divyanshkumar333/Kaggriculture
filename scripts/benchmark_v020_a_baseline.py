from benchmark_v020_suite import run_matchup
import json

SEEDS = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]

OPPONENTS = {
    "Self (V020-A)": "agents/v020_a_control.py",
    "Diversified (V004-B)": "agents/v004_b_diversify.py",
    "Animal (V005-D)": "agents/v005_d_combined.py",
    "Dynamic Clusters (V008-D)": "agents/v008_d_dynamic_clusters.py",
    "Harvest Timing (V009-B)": "agents/v009_b_harvest_timing.py",
    "Melon Maxxer": "agents/melon_maxxer.py",
    "Melon Flooder": "agents/opp_melon_flooder.py",
    "Balanced Optimizer": "agents/opp_balanced_optimizer.py",
    "Starter": "starter",
    "Random": "random"
}

def benchmark_control():
    print("==================================================")
    print("RUNNING V020-A CONTROL BASELINE BENCHMARK")
    print(f"Seeds: {len(SEEDS)} per opponent")
    print("==================================================")
    
    summary = {}
    total_wins = 0
    total_matches = 0
    all_banks = []
    
    for name, opp_path in OPPONENTS.items():
        if name == "Self (V020-A)":
            # For self-play, run against itself
            res = run_matchup("agents/v020_a_control.py", "agents/v020_a_control.py", SEEDS)
        else:
            res = run_matchup("agents/v020_a_control.py", opp_path, SEEDS)
            
        summary[name] = res
        total_wins += res["wins"]
        total_matches += res["total"]
        all_banks.extend([r["reward_a"] for r in res["results"]])
        
        print(f"vs {name:<26} | Win Rate: {res['win_rate']:5.1f}% ({res['wins']:2d}W/{res['losses']:2d}L/{res['ties']:2d}T) | Bank: ${res['mean_a']:6.0f} | Opp: ${res['mean_b']:6.0f} | Delta: ${res['delta']:+6.0f} | Min: ${res['min_a']:6.0f}")

    overall_win_rate = (total_wins / total_matches) * 100
    mean_bank = sum(all_banks) / len(all_banks)
    min_bank = min(all_banks)
    
    print("\n==================================================")
    print(f"OVERALL V020-A CONTROL: Win Rate: {overall_win_rate:.1f}% | Mean Bank: ${mean_bank:.0f} | Worst Case: ${min_bank:.0f}")
    print("==================================================")
    
    with open("experiments/v020_a_baseline.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    benchmark_control()
