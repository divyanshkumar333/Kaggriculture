import json
import glob
import numpy as np
import os
import subprocess
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--agent", default="agents/v009_a_control.py")
parser.add_argument("--games", default="5")
args = parser.parse_args()

# Run games
print(f"Running {args.games} games of {args.agent} vs random")
subprocess.run([
    sys.executable, "experiments.py",
    "--agent", args.agent,
    "--opponent", "random",
    "--games", args.games,
    "--steps", "720",
    "--seed_start", "800",
    "--output", "experiments/v009_analysis_results.json"
])

print("Analysis run complete. Reading metrics...")

# Read the metrics JSONs
metric_files = []
for i in range(5):
    seed = 800 + i
    # We don't know if the agent is p0 or p1, so check both
    if os.path.exists(f"experiments/metrics/game_{seed}_p0.json"):
        metric_files.append(f"experiments/metrics/game_{seed}_p0.json")
    elif os.path.exists(f"experiments/metrics/game_{seed}_p1.json"):
        metric_files.append(f"experiments/metrics/game_{seed}_p1.json")

metrics = []
for f in metric_files:
    with open(f, 'r') as fp:
        metrics.append(json.load(fp))

if not metrics:
    print("No metrics found!")
    exit(1)

# Analyze bottlenecks
avg_deaths = np.mean([m['crops']['WHEAT']['deaths'] + m['crops'].get('MELON', {}).get('deaths', 0) for m in metrics])
avg_water_miss = np.mean([m['water']['misses'] for m in metrics])
avg_movement = np.mean([m['workers']['movement_actions'] + m['farmer']['movement_actions'] for m in metrics])
avg_useful = np.mean([m['workers']['useful_actions'] + m['farmer']['useful_actions'] for m in metrics])
avg_worker_spending = np.mean([m['economy']['worker_spending'] for m in metrics])
avg_seed_spending = np.mean([m['economy']['seed_spending'] for m in metrics])
avg_idle = np.mean([m['workers']['idle_turns'] for m in metrics])
avg_surplus = np.mean([m['labor']['surplus_sum'] for m in metrics])
avg_deficit = np.mean([m['labor']['deficit_sum'] for m in metrics])
avg_revenue = np.mean([m['economy']['total_revenue'] for m in metrics])

# Output bottleneck breakdown
print("=== BOTTLENECK ANALYSIS ===")
print(f"Crop Deaths: {avg_deaths}")
print(f"Watering Misses: {avg_water_miss}")
print(f"Movement Actions: {avg_movement}")
print(f"Useful Actions: {avg_useful}")
print(f"Worker Spending: {avg_worker_spending}")
print(f"Seed Spending: {avg_seed_spending}")
print(f"Idle Turns: {avg_idle}")
print(f"Labor Surplus: {avg_surplus}")
print(f"Labor Deficit: {avg_deficit}")
print(f"Total Revenue: {avg_revenue}")

# Estimate losses
# Crop deaths: ~ $100 profit per crop
loss_deaths = avg_deaths * 100
# Movement efficiency loss (compared to hypothetical 100% efficiency, but say reclaim 20% of movement)
movement_pct = avg_movement / (avg_movement + avg_useful) if avg_movement + avg_useful > 0 else 0
print(f"Movement Efficiency: {1 - movement_pct:.2f}")

loss_movement = (avg_movement * 0.1) * 15 # 10% of movement turns reclaimed * $15 per action
loss_idle = avg_idle * 15 # Idle turn = wasted action
loss_water_miss = avg_water_miss * 20 # 1 miss = 1 yield lost for some crops

print(f"Estimated Loss - Crop Deaths: ${loss_deaths:.2f}")
print(f"Estimated Loss - Movement (10% reclaim): ${loss_movement:.2f}")
print(f"Estimated Loss - Idle Workers: ${loss_idle:.2f}")
print(f"Estimated Loss - Watering Misses: ${loss_water_miss:.2f}")
