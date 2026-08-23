# V001 Spatial Experiment Results

## Objective
To determine if adding a spatial locality scoring system (preferring nearby tasks) improves worker efficiency, reduces wasted movement, and makes land expansion economically viable in Kaggriculture.

## Methodology
A 270-game benchmark was run (30 games vs `random`, `starter`, and `melon_maxxer` for 3 variants). 

*   **Variant A (Control)**: `v001_baseline.py` - Tasks strictly sorted by `(priority, distance)`.
*   **Variant B (Locality)**: `v001_locality.py` - Tasks scored via `urgency + economic_value - distance`.
*   **Variant C (Locality + Expansion)**: `v001_expansion_locality.py` - Adds a strict `50.0` travel penalty if a worker takes a task outside their assigned quadrant. Land expansion enabled.

## Results (270 Game Averages)

| Metric | Variant A | Variant B | Variant C |
|---|---|---|---|
| Final Bank | **$28,140** | $28,072 | $1,760 |
| Win Rate | **100.0%** | **100.0%** | 40.0% |
| Crop Deaths | **9.8** | 10.2 | 0.0 |
| Avg Assignment Distance | **1.62** | 1.80 | 0.00 |
| Movement Efficiency | **22.0%** | 19.9% | 17.4% |
| Melons Planted | 61.7 | 63.8 | 42.9 |
| Melons Harvested | 36.9 | 39.0 | 5.4 |
| Worker Idle Turns | 2,332 | 2,072 | 423 |
| Movement Actions | 1,394 | 1,548 | 530 |
| Useful Actions | 394 | 385 | 112 |
| Total Revenue | $32,351 | $32,405 | $4,524 |
| Total Spending | $6,009 | $6,097 | $5,727 |
| Worker Cost | $963 | $893 | $199 |
| Land Cost | $0 | $0 | $2,022 |
| Land Purchased | 0.0 | 0.0 | 1.4 |

## Analysis

### Q1: Does locality improve the existing 5x5 farm?
**No.** Variant B performed slightly worse than Variant A across almost all metrics. The final bank was slightly lower, and crop deaths actually increased.

### Q2: Does locality reduce movement waste?
**No.** Paradoxically, Variant B *increased* movement actions (1,394 -> 1,548) and *increased* the average assignment distance (1.62 -> 1.80) while decreasing overall movement efficiency.
*Why?* The greedy locality heuristic likely causes a "stranding" effect. If workers prioritize nearby tasks over urgent tasks, they leave urgent, far-away tasks stranded. Eventually, those stranded tasks must be completed, forcing a worker to cross the entire map. By breaking the strict priority queue, the agent lost the structural efficiency of doing the most important things first, without actually gaining spatial coherence.

### Q3: Does locality make expansion economically viable?
**No.** Variant C catastrophically failed (Final Bank dropped to $1,760). The regional assignment penalty likely meant that when one quadrant had too much work, workers in other quadrants preferred to stay idle (or do low-value tasks) rather than cross the regional boundary to help. The lack of cross-region cooperation led to massive economic losses and low harvest volumes. 

## Conclusion and Next Steps (Step 6G/J)

The greedy `score = urgency + value - distance` heuristic is insufficient. It is highly likely that **Optuna hyperparameter tuning will NOT solve this**, because the fundamental architecture (individual workers greedily claiming tasks) is the root cause of the stranding effect and poor global routing.

To fix the spatial bottleneck and eventually enable land expansion, we need a better multi-agent scheduling algorithm rather than just tweaking local weights. (e.g., globally minimizing travel cost for the whole fleet, or zone-defense with dynamic load balancing).
