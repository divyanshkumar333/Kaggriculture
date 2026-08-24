import json
import statistics
from collections import defaultdict

def generate_report():
    try:
        with open("experiments/v007_benchmark_results.json", "r") as f:
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
        "# V007 Spatial Planting Experiment Report",
        "",
        "## Benchmark Results (Mean Final Bank)",
        ""
    ]

    variants = ["v007_a_control", "v007_b_clustered", "v007_c_sector_planting"]
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
        "### Q1: Did V007-B (Clustered Planting) successfully reduce Spatial Fragmentation?",
        "- To be analyzed from analyze_bottlenecks.py",
        "",
        "### Q2: Did V007-C (Sector Planting) further optimize the spatial distribution?",
        "- To be analyzed.",
        "",
        "### Q3: Did clustered planting translate to higher Movement Efficiency or lower Movement Actions?",
        "- To be analyzed.",
        "",
        "### Q4: Did clustered planting prevent Crop Deaths from missed waterings?",
        "- To be analyzed.",
        "",
        "### Q5: Did either variant successfully improve Final Bank vs the V007-A Control?",
        "- To be analyzed."
    ])

    with open("V007_SPATIAL_PLANTING_EXPERIMENT.md", "w") as f:
        f.write("\n".join(report_lines))

    print("Generated V007_SPATIAL_PLANTING_EXPERIMENT.md")

if __name__ == "__main__":
    generate_report()
