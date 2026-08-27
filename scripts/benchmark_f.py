import os
import sys
import numpy as np

# Add the scripts directory to the path so we can import v018_runner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import v018_runner

def main():
    print("==============================")
    print("Starting 120-game Benchmark: V018-B vs V018-F")
    print("40 seeds x 3 opponents (random, starter, pass)")
    print("==============================")
    
    variants_data = {}
    opps = ["random", "pass", "starter"]
    num_seeds = 40
    
    print("Running V018-B...")
    r_b, m_b = v018_runner.analyze_benchmark(
        "agents/v018_b_batch_cap.py", 
        opps, 
        num_seeds, 
        {"V018_B_CAP": "4"}
    )
    variants_data["V018-B"] = {"rewards": r_b, "metrics": m_b}
    
    print("Running V018-F...")
    r_f, m_f = v018_runner.analyze_benchmark(
        "agents/v018_f_subsistence_fixed.py", 
        opps, 
        num_seeds, 
        {"V018_B_CAP": "4", "V018_F_FALLBACK_TRIGGER": "10"}
    )
    variants_data["V018-F"] = {"rewards": r_f, "metrics": m_f}

    # Generate custom report
    print("\n\n" + "="*70)
    print("BENCHMARK RESULTS")
    print("="*70)

    for name, data in variants_data.items():
        arr = np.array(data["rewards"])
        print(f"\n{name} Performance:")
        print(f"  Mean Score: ${np.mean(arr):.2f}")
        print(f"  Median:     ${np.median(arr):.2f}")
        print(f"  Std Dev:    ${np.std(arr):.2f}")
        
        # Calculate win rates vs opponents (assuming simple tracking since analyze_benchmark just runs)
        # analyze_benchmark runs tasks in order: opp1(seed0..39), opp2(seed0..39), opp3(seed0..39)
        if len(arr) == len(opps) * num_seeds:
            for i, opp in enumerate(opps):
                opp_arr = arr[i*num_seeds:(i+1)*num_seeds]
                print(f"  vs {opp:<8}: ${np.mean(opp_arr):.2f} mean")

    # Win rate of F vs B (paired by seed)
    if len(variants_data["V018-B"]["rewards"]) == len(variants_data["V018-F"]["rewards"]):
        f_wins = 0
        ties = 0
        for b_score, f_score in zip(variants_data["V018-B"]["rewards"], variants_data["V018-F"]["rewards"]):
            if f_score > b_score:
                f_wins += 1
            elif f_score == b_score:
                ties += 1
        total = len(variants_data["V018-F"]["rewards"])
        print(f"\nDirect Head-to-Head (paired by seed/opponent):")
        print(f"  V018-F Wins: {f_wins} / {total} ({(f_wins/total)*100:.1f}%)")
        print(f"  Ties:        {ties} / {total} ({(ties/total)*100:.1f}%)")
        print(f"  V018-B Wins: {total - f_wins - ties} / {total} ({((total - f_wins - ties)/total)*100:.1f}%)")

if __name__ == "__main__":
    main()
