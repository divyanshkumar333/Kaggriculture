# V006 Bottleneck Analysis

## Comprehensive Audit
Using the deep telemetry generated during the `run_unified.py` benchmark, we audited the performance of the True Champion (V004-B) to identify the largest remaining source of lost Final Bank.

| Metric | V004-B (Champion) |
|---|---|
| Mean Final Bank | $33,465.82 |
| Worker Utilization | 89.3% |
| Movement Efficiency | **47.8%** |
| Avg Labor Deficit | 759 actions/game |
| Avg Labor Surplus | **3,954 actions/game** |
| Avg Crop Deaths | 11.8 / game |
| Avg Water Misses | 8.7 / game |

## Root Cause of Lost Profit
The data clearly shows that **Spatial Task Fragmentation (Movement/Logistics)** is the primary bottleneck.

### 1. Movement Inefficiency (Rank #1)
- The agent's Movement Efficiency is only 47.8%. This means that over 52% of all worker turns are spent moving (`NORTH`, `SOUTH`, `EAST`, `WEST`) or passing (`PASS`), rather than executing useful actions (`WATER`, `HARVEST`, `PLANT`).
- Simultaneously, the agent records an average **Labor Surplus of 3,954 turns**, while missing critical tasks resulting in a **Labor Deficit of 759 turns**. 
- The agent has *more than enough* aggregate labor to cover all tasks, but the `TaskAllocator` utilizes a greedy Hungarian matrix minimizing immediate distance. As the farm expands, tasks become scattered across the 10x10 board. Workers oscillate back and forth across the board to chase high-priority tasks rather than clearing a local cluster of tasks.
- **Estimated Lost Profit:** Reclaiming just 10% of the 3,954 wasted movement turns (at the marginal worker ROI of $15/action) equates to **~$6,000 in lost Final Bank**.

### 2. Crop Deaths (Rank #2)
- An average of 11.8 crops die per game due to missed watering. 
- **Estimated Lost Profit:** At ~$100 net profit per crop, this is **~$1,180 in lost Final Bank**.
- This is a direct symptom of Bottleneck #1 (workers spend too much time walking and miss the watering deadline).

## Conclusion
The single most impactful optimization that can be made is to improve the `TaskAllocator`'s pathing and assignment logic to cluster tasks geographically. We will formulate V006 experiments focused purely on this structural bottleneck.
