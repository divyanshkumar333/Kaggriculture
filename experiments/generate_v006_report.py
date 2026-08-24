import json
import statistics
from collections import defaultdict

def generate_report():
    try:
        with open("experiments/v006_benchmark_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Run experiments/run_v006_benchmark.py first.")
        return

    # Group results by variant and opponent
    data = defaultdict(lambda: defaultdict(list))
    for r in results:
        if "error" not in r:
            data[r["variant"]][r["opponent"]].append(r["p1_money"])

    report_lines = [
        "# V006 Logistical Optimization Experiment Report",
        "",
        "## Benchmark Results (Mean Final Bank)",
        ""
    ]

    variants = ["v006_a_control", "v006_b_sectors", "v006_c_tsp"]
    opponents = ["random", "starter", "melon_maxxer"]

    for var in variants:
        report_lines.append(f"### {var}")
        all_scores = []
        for opp in opponents:
            scores = data[var].get(opp, [])
            if scores:
                mean_score = statistics.mean(scores)
                report_lines.append(f"- vs {opp}: ${mean_score:.2f} (n={len(scores)})")
                all_scores.extend(scores)
        if all_scores:
            report_lines.append(f"**Overall Mean: ${statistics.mean(all_scores):.2f}**")
        report_lines.append("")

    report_lines.extend([
        "## Analysis",
        "",
        "### Q1: Does V006-B (Sector Constraints) improve movement efficiency?",
        "- To be analyzed.",
        "",
        "### Q2: Does V006-B (Sector Constraints) leave tasks uncompleted if a sector gets overloaded?",
        "- To be analyzed.",
        "",
        "### Q3: Does V006-C (TSP / Non-Linear Distance) successfully cluster worker tasks?",
        "- To be analyzed.",
        "",
        "### Q4: Which variant achieves the highest Mean Final Bank, and does it exceed V004-B ($33,465)?",
        "- To be analyzed."
    ])

    with open("V006_EXPERIMENT.md", "w") as f:
        f.write("\n".join(report_lines))

    print("Generated V006_EXPERIMENT.md")

if __name__ == "__main__":
    generate_report()
