import subprocess
import itertools
import json

agents = [
    "main.py",
    "agents/v025_a_aggressive_cows.py",
    "agents/v057_generalized_spoiler.py",
    "agents/v085_grandmaster_roi.py"
]

results = {}

for a1, a2 in itertools.permutations(agents, 2):
    print(f"Running {a1} vs {a2} (16 seeds)...")
    res = subprocess.run(
        ['.venv\Scripts\python.exe', 'scripts/bench_paired.py', a1, a2, '--seeds', '16', '--workers', '8'],
        capture_output=True, text=True
    )
    
    # Parse output to find win rate
    # Expected output contains: "Win Rate: X / 32 (Y%)"
    # Actually bench_paired outputs "Paired win rate: "
    wr_line = [line for line in res.stdout.split('\n') if "Paired win rate:" in line]
    if wr_line:
        print(f"  {wr_line[0]}")
        results[f"{a1} vs {a2}"] = wr_line[0]
    else:
        print(f"  Failed to parse output")

    with open('RESEARCH/nxn_results.json', 'w') as f:
        json.dump(results, f, indent=2)

print("Saved to RESEARCH/nxn_results.json")
