import os
import sys
import json
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from tournament_harness import run_paired_tournament

def run_benchmarks():
    agent_v053 = "agents/v053_market_adaptive.py"
    agent_v051 = "agents/v051_v16_lookahead30_final.py"
    agent_v16 = "agents/public_v16_rc5.py"
    agent_v027 = "agents/v027_hierarchical_meta.py"
    agent_v025a = "agents/public_v27_reset.py"  # Assumed from past logs to be V025-A

    seeds = list(range(10000, 10050))  # 50 seeds = 100 matches

    results_dir = os.path.join("RESEARCH", "benchmark_history")
    os.makedirs(results_dir, exist_ok=True)

    matchups = [
        ("V053_MarketAdaptive", agent_v053, "V051_Final", agent_v051),
        ("V053_MarketAdaptive", agent_v053, "V16_Public", agent_v16),
        ("V053_MarketAdaptive", agent_v053, "V027_Base", agent_v027),
        ("V053_MarketAdaptive", agent_v053, "V025_A", agent_v025a),
    ]

    for label_a, path_a, label_b, path_b in matchups:
        print(f"\\n{'='*50}")
        print(f"Starting benchmark: {label_a} vs {label_b}")
        print(f"{'='*50}\\n")
        
        if not os.path.exists(path_b):
            print(f"WARNING: Opponent {path_b} not found. Skipping.")
            continue
            
        summary = run_paired_tournament(
            path_a, path_b, seeds,
            label_a=label_a, label_b=label_b,
            max_workers=6
        )
        
        timestamp = int(time.time())
        filename = f"{label_a}_vs_{label_b}_500p_{timestamp}.json"
        out_path = os.path.join(results_dir, filename)
        
        with open(out_path, "w") as f:
            json.dump(summary, f, indent=2)
            
        print(f"Saved results to {out_path}\\n")

if __name__ == "__main__":
    run_benchmarks()
