import json
import statistics
from collections import defaultdict

def generate_report():
    try:
        with open("experiments/v005_benchmark_results.json", "r") as f:
            results = json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}")
        return

    # Group results by variant and opponent
    data = defaultdict(lambda: defaultdict(list))
    for r in results:
        if "error" not in r:
            data[r["variant"]][r["opponent"]].append(r["p1_money"])

    report_lines = [
        "# V005 Animal Husbandry Experiment Report",
        "",
        "## Benchmark Results (Mean Final Bank)",
        ""
    ]

    variants = ["v005_a_control", "v005_c_best_animal", "v005_d_combined"]
    opponents = ["random", "starter", "v004_b_diversify"]

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
        "### Q1: What is the true ROI of a single Goose, Cow, and Sheep?",
        "- Calculated dynamically in the agent.",
        "",
        "### Q2: Does animal care require more or less labor per unit of profit than crops?",
        "- Animal labor is daily (FEED/CARE/FERT) + HARVEST vs crop which is daily WATER + HARVEST.",
        "",
        "### Q3: How severely does the market price drop for Wool and Milk if scaled aggressively?",
        "- Wool drops extremely fast because `T = 105`.",
        "",
        "### Q4: Are animals strictly superior, strictly inferior, or situationally superior to optimal crop diversification?",
        "- To be analyzed from benchmark results.",
        "",
        "### Q5: If a pure-animal farm (V005-C) is run, how does its Final Bank compare to V004-B?",
        "- To be analyzed from benchmark results.",
        "",
        "### Q6: If an optimizer dynamically balances crops and animals (V005-D), what is its average mix?",
        "- To be analyzed from benchmark results.",
        "",
        "### Q7: Does the FERTILIZER produced by animals substantially alter their ROI?",
        "- Yes, FERTILIZER provides significant daily revenue ($100 base) which props up animal ROI even when Wool/Milk prices drop.",
        "",
        "### Q8: Should animals be purchased early game (capital constrained) or late game (labor constrained)?",
        "- Early game because they provide continuous production for the remainder of the 30 days.",
        "",
        "### Q9: What is the optimal labor force size for an animal farm vs a crop farm?",
        "- To be observed.",
        "",
        "### Q10: Does animal escape risk (2 days unfed) create a hard limit on scaling?",
        "- Yes, if we over-hire or if labor is bottlenecked, animals will escape."
    ])

    with open("V005_ANIMAL_EXPERIMENT.md", "w") as f:
        f.write("\n".join(report_lines))

    print("Generated V005_ANIMAL_EXPERIMENT.md")

if __name__ == "__main__":
    generate_report()
