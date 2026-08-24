# V009 Smoke Test Report

## V009-A (Control)
```
Running 5 games: agents/v009_a_control.py vs random
Game 1/5 (Seed 800): agents/v009_a_control.py $36611.0 vs random $0 -> Winner: agents/v009_a_control.py
Game 2/5 (Seed 801): agents/v009_a_control.py $35419.0 vs random $0 -> Winner: agents/v009_a_control.py
Game 3/5 (Seed 802): agents/v009_a_control.py $33835.0 vs random $40.0 -> Winner: agents/v009_a_control.py
Game 4/5 (Seed 803): agents/v009_a_control.py $35642.0 vs random $0 -> Winner: agents/v009_a_control.py
Game 5/5 (Seed 804): agents/v009_a_control.py $34071.0 vs random $0 -> Winner: agents/v009_a_control.py

--- Final Statistics ---
Total Games: 5
agents/v009_a_control.py Wins: 5 (100.0%)
random Wins: 0 (0.0%)
Ties: 0
Errors/Crashes: 0

agents/v009_a_control.py Performance:
  Mean:   $35115.60
  Median: $35419.00
  StdDev: $1033.10
  Min:    $33835.00
  Max:    $36611.00

random Performance:
  Mean:   $8.00
  Median: $0.00
  StdDev: $16.00
  Min:    $0.00
  Max:    $40.00

Results saved to experiments/v009_analysis_results.json
Scorecard saved to experiments/v009_analysis_results.md
Running 5 games of agents/v009_a_control.py vs random
Analysis run complete. Reading metrics...
=== BOTTLENECK ANALYSIS ===
Crop Deaths: 0.0
Watering Misses: 4.4
Movement Actions: 798.0
Useful Actions: 764.8
Worker Spending: 74.0
Seed Spending: 4860.0
Idle Turns: 185.2
Labor Surplus: 6895.6
Labor Deficit: 914.8
Total Revenue: 37882.8
Movement Efficiency: 0.49
Estimated Loss - Crop Deaths: $0.00
Estimated Loss - Movement (10% reclaim): $1197.00
Estimated Loss - Idle Workers: $2778.00
Estimated Loss - Watering Misses: $88.00
```

## V009-B (Harvest Timing Fix)
```
Running 5 games: agents/v009_b_harvest_timing.py vs random
Game 1/5 (Seed 800): agents/v009_b_harvest_timing.py $38216.0 vs random $0 -> Winner: agents/v009_b_harvest_timing.py
Game 2/5 (Seed 801): agents/v009_b_harvest_timing.py $37330.0 vs random $0 -> Winner: agents/v009_b_harvest_timing.py
Game 3/5 (Seed 802): agents/v009_b_harvest_timing.py $36838.0 vs random $0 -> Winner: agents/v009_b_harvest_timing.py
Game 4/5 (Seed 803): agents/v009_b_harvest_timing.py $37009.0 vs random $0 -> Winner: agents/v009_b_harvest_timing.py
Game 5/5 (Seed 804): agents/v009_b_harvest_timing.py $41270.0 vs random $0 -> Winner: agents/v009_b_harvest_timing.py

--- Final Statistics ---
Total Games: 5
agents/v009_b_harvest_timing.py Wins: 5 (100.0%)
random Wins: 0 (0.0%)
Ties: 0
Errors/Crashes: 0

agents/v009_b_harvest_timing.py Performance:
  Mean:   $38132.60
  Median: $37330.00
  StdDev: $1639.08
  Min:    $36838.00
  Max:    $41270.00

random Performance:
  Mean:   $0.00
  Median: $0.00
  StdDev: $0.00
  Min:    $0.00
  Max:    $0.00

Results saved to experiments/v009_analysis_results.json
Scorecard saved to experiments/v009_analysis_results.md
Running 5 games of agents/v009_b_harvest_timing.py vs random
Analysis run complete. Reading metrics...
=== BOTTLENECK ANALYSIS ===
Crop Deaths: 0.0
Watering Misses: 5.4
Movement Actions: 804.6
Useful Actions: 801.6
Worker Spending: 79.6
Seed Spending: 4430.0
Idle Turns: 209.8
Labor Surplus: 7080.0
Labor Deficit: 1002.6
Total Revenue: 40489.4
Movement Efficiency: 0.50
Estimated Loss - Crop Deaths: $0.00
Estimated Loss - Movement (10% reclaim): $1206.90
Estimated Loss - Idle Workers: $3147.00
Estimated Loss - Watering Misses: $108.00
```
