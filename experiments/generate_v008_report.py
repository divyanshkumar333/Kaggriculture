import json
import statistics
from collections import defaultdict

def generate_report():
    try:
        with open("experiments/v008_benchmark_results.json", "r") as f:
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
        "# V008 Adaptive Production Clustering Experiment Report",
        "",
        "## Benchmark Results (Mean Final Bank)",
        ""
    ]

    variants = ["v008_a_control", "v008_b_adaptive_cluster", "v008_c_task_density", "v008_d_dynamic_clusters"]
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
        "### Q1: Did V008-B (Adaptive Cluster) successfully create multiple healthy clusters instead of one mega-cluster?",
        "- To be analyzed from analyze_bottlenecks.py",
        "",
        "### Q2: Did V008-C (Task Density) improve economic alignment without increasing crop deaths?",
        "- To be analyzed.",
        "",
        "### Q3: Did V008-D (Dynamic Clusters) successfully adjust cluster count based on labor surplus/deficit?",
        "- To be analyzed.",
        "",
        "### Q4: Did Adaptive Clustering lower the average task distance and reduce watering misses compared to V008-A?",
        "- To be analyzed.",
        "",
        "### Q5: Which variant successfully improved Final Bank vs the V008-A Control?",
        "- To be analyzed."
    ])

    with open("V008_CLUSTERING_EXPERIMENT.md", "w") as f:
        f.write("\n".join(report_lines))

    print("Generated V008_CLUSTERING_EXPERIMENT.md")

if __name__ == "__main__":
    generate_report()
