import os
import json
import numpy as np
from scripts.fast_tournament import run_fast_tournament

def main():
    agents = {
        "A (V104 Base)": "submission_v104_quote_priority.py",
        "B (No Quote Priority)": "agents/ablations/v104_minus_b_quote_priority.py",
        "C (No Care Gating)": "agents/ablations/v104_minus_c_care_gating.py",
        "D (No CTRTABLE)": "agents/ablations/v104_minus_d_ctrtable.py",
        "E (No Terminal Liq)": "agents/ablations/v104_minus_e_terminal.py",
        "F (No Reflex Layers)": "agents/ablations/v104_minus_f_reflex_layers.py",
        "G (V118)": "agents/v118_optimal_liquidation.py",
    }

    # Diverse strong opponents
    opponents = [
        "agents/v099_adaptive_master.py",
        "agents/v080_omni_spoiler.py",
        "agents/v100b_gm_fixed_opening.py",
        "agents/v116_carrot_margin_optimized.py"
    ]

    # Use enough fresh seeds
    num_seeds = 10
    seeds = list(range(9900, 9900 + num_seeds))

    results = {}

    print(f"Running tournament with {len(seeds)} seeds * 2 seats * {len(opponents)} opponents = {len(seeds)*2*len(opponents)} games per candidate.")

    for name, cand_path in agents.items():
        print(f"\nTesting {name}...")
        try:
            summary, overall_wr, overall_margin = run_fast_tournament(
                cand_path, opponents, seeds=seeds, max_workers=6
            )
            print(f"{name} WR: {overall_wr:.1f}%, Margin: {overall_margin:.1f}")
            results[name] = {
                "win_rate": overall_wr,
                "margin": overall_margin,
                "details": summary
            }
        except Exception as e:
            print(f"Failed to test {name}: {e}")

    with open("reports/ablation_tournament_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n--- Summary ---")
    for name, data in results.items():
        if "win_rate" in data:
            print(f"{name}: WR={data['win_rate']:.1f}%, Margin={data['margin']:.1f}")
        else:
            print(f"{name}: FAILED")

if __name__ == "__main__":
    main()
