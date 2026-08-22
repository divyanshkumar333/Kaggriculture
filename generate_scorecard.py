import json
import glob
import os

def main():
    json_files = glob.glob("experiments/benchmarks/*.json")
    combined = []
    
    md_content = "# V001 Baseline Benchmark Report\n\n"
    md_content += "| Agent | Opponent | Games | Win % | Avg Bank | Median | Std | Min | Max |\n"
    md_content += "| ----- | -------- | ----: | ----: | -------: | -----: | --: | --: | --: |\n"
    
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)
            combined.append(data)
            
            agent = data["agent1"]
            opponent = data["agent2"]
            games = data["games"]
            wins = data["wins_a1"]
            win_pct = (wins / max(1, games)) * 100
            
            stats = data.get("stats_a1", {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0})
            md_content += f"| {agent} | {opponent} | {games} | {win_pct:.1f}% | ${stats['mean']:.2f} | ${stats['median']:.2f} | ${stats['std']:.2f} | ${stats['min']:.2f} | ${stats['max']:.2f} |\n"
            
    os.makedirs("experiments", exist_ok=True)
    with open("experiments/benchmark_report.json", "w") as f:
        json.dump(combined, f, indent=2)
        
    with open("experiments/benchmark_report.md", "w") as f:
        f.write(md_content)
        
    print("Combined scorecard generated successfully.")

if __name__ == "__main__":
    main()
