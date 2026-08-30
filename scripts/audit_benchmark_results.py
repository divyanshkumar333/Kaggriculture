import json
import numpy as np

def audit_results():
    print("==================================================")
    print("INDEPENDENT AUDIT OF BENCHMARK RESULT JSON FILES")
    print("==================================================")
    
    with open("experiments/v020_c_benchmark.json", "r") as f:
        data_c = json.load(f)
        
    with open("experiments/v020_a_baseline.json", "r") as f:
        data_a = json.load(f)
        
    print(f"Opponents evaluated in V020-C: {list(data_c.keys())}")
    
    total_games = 0
    total_wins = 0
    total_losses = 0
    total_ties = 0
    all_banks_c = []
    all_banks_opp = []
    
    for opp_name, stats in data_c.items():
        results = stats["results"]
        n = len(results)
        total_games += n
        
        # Verify seeds
        seeds = [r["seed"] for r in results]
        expected_seeds = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
        assert seeds == expected_seeds, f"Seed mismatch for {opp_name}: {seeds}"
        
        # Verify alternation
        alternation = [r["p0_is_a"] for r in results]
        expected_alt = [(i % 2 == 0) for i in range(12)]
        assert alternation == expected_alt, f"Alternation mismatch for {opp_name}"
        
        # Recalculate outcomes directly from rewards
        wins = 0
        losses = 0
        ties = 0
        banks_a = []
        banks_b = []
        
        for r in results:
            ra = float(r["reward_a"])
            rb = float(r["reward_b"])
            banks_a.append(ra)
            banks_b.append(rb)
            all_banks_c.append(ra)
            all_banks_opp.append(rb)
            
            if ra > rb:
                wins += 1
                assert r["outcome"] == "WIN", f"Recorded outcome {r['outcome']} does not match reward: ra={ra}, rb={rb}"
            elif ra < rb:
                losses += 1
                assert r["outcome"] == "LOSS", f"Recorded outcome {r['outcome']} does not match reward: ra={ra}, rb={rb}"
            else:
                ties += 1
                assert r["outcome"] == "TIE", f"Recorded outcome {r['outcome']} does not match reward: ra={ra}, rb={rb}"
                
        total_wins += wins
        total_losses += losses
        total_ties += ties
        
        recalc_mean_a = float(np.mean(banks_a))
        recalc_mean_b = float(np.mean(banks_b))
        recalc_min_a = float(np.min(banks_a))
        recalc_max_a = float(np.max(banks_a))
        
        assert abs(recalc_mean_a - stats["mean_a"]) < 1e-4, f"Mean mismatch for {opp_name}"
        assert abs(recalc_mean_b - stats["mean_b"]) < 1e-4, f"Mean opp mismatch for {opp_name}"
        assert abs(recalc_min_a - stats["min_a"]) < 1e-4, f"Min mismatch for {opp_name}"
        
        win_rate = (wins / n) * 100
        print(f"  {opp_name:<26} | Games: {n:2d} | Wins: {wins:2d} | Losses: {losses:2d} | Ties: {ties:2d} | Win Rate: {win_rate:5.1f}% | Mean Bank: ${recalc_mean_a:6.0f} | Opp: ${recalc_mean_b:6.0f} | Min: ${recalc_min_a:6.0f}")

    print("\n--- INDEPENDENT TOTALS ---")
    overall_win_rate = (total_wins / total_games) * 100
    overall_mean_c = float(np.mean(all_banks_c))
    overall_median_c = float(np.median(all_banks_c))
    overall_min_c = float(np.min(all_banks_c))
    overall_max_c = float(np.max(all_banks_c))
    overall_mean_opp = float(np.mean(all_banks_opp))
    
    print(f"Total Games Completed: {total_games}")
    print(f"Total Wins:            {total_wins}")
    print(f"Total Losses:          {total_losses}")
    print(f"Total Ties:            {total_ties}")
    print(f"Overall Win Rate:      {overall_win_rate:.2f}% ({total_wins}/{total_games})")
    print(f"Mean Final Bank:       ${overall_mean_c:,.2f}")
    print(f"Median Final Bank:     ${overall_median_c:,.2f}")
    print(f"Worst-Case Bank Floor: ${overall_min_c:,.2f}")
    print(f"Max Final Bank:        ${overall_max_c:,.2f}")
    print(f"Mean Opponent Bank:    ${overall_mean_opp:,.2f}")
    print(f"Bank Advantage:        ${overall_mean_c - overall_mean_opp:+,.2f}")
    print("==================================================")
    print("ALL INTEGRITY CHECKS PASSED: BENCHMARK IS 100% VALID")
    print("==================================================")

if __name__ == "__main__":
    audit_results()
