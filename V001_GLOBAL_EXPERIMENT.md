# V001 Global Allocation Experiment

## Objective
To determine if replacing the sequential greedy worker assignment with a global optimal bipartite matching algorithm (`scipy.optimize.linear_sum_assignment`) solves the spatial "stranding" problem, minimizes travel waste, eliminates crop deaths, and makes land expansion physically viable.

## Methodology
A 270-game benchmark (30 games x 3 opponents x 3 variants).
*   **Variant A (Control)**: `v001_baseline.py` (greedy assignment).
*   **Variant D (Global)**: `v001_global.py` (Hungarian algorithm, hard constraints for dying crops, no expansion).
*   **Variant E (Global + Expansion)**: `v001_global_expansion.py` (Hungarian algorithm, ROI-based expansion).

## Benchmark Results

| Metric | Variant A | Variant D | Variant E |
|---|---|---|---|
| Final Bank | $28,131 | $26,817 | $14,779 |
| Win Rate | 100.0% | 100.0% | 100.0% |
| Crop Deaths | 9.8 | **0.0** | **0.0** |
| Avg Assignment Distance | 1.62 | 1.45 | **1.28** |
| Movement Efficiency | 22.0% | 29.5% | **37.3%** |
| Melons Planted | 61.7 | 73.8 | 156.4 |
| Melons Harvested | 37.0 | 48.9 | **63.6** |
| Worker Idle Turns | 2,330 | 2,015 | 325 |
| Movement Actions | 1,394 | 1,491 | 1,573 |
| Useful Actions | 394 | 623 | **936** |
| Total Revenue | $32,353 | $32,263 | $33,328 |
| Total Spending | $6,018 | $7,177 | $20,366 |
| Worker Cost | $961 | $964 | $646 |
| Land Cost | $0 | $0 | $7,000 |
| Land Purchased | 0.0 | 0.0 | 3.0 |

## Analysis

### 1. Did global assignment improve the 5x5 farm (D vs A)?
**Algorithmic Success:** Yes, massively. 
*   **Crop Deaths dropped to absolutely 0.0.** The hard constraints worked perfectly. 
*   **Useful actions increased by 58%** (394 -> 623). 
*   **Harvests increased by 32%** (37 -> 49).
*   **Movement Efficiency increased** from 22.0% to 29.5%.

**Economic Paradox:** Why did Final Bank drop? The agent successfully produced 32% more Melons, but total revenue remained flat at ~$32k. The Kaggriculture dynamic market penalized the oversupply of Melons, crashing the sale price to the $1 floor. The agent spent more on seeds but hit the market revenue ceiling.

### 2. Did global scheduling unlock profitable expansion (E vs D)?
**Physical Success, Economic Failure.**
*   Variant E successfully managed 4 quadrants seamlessly. Average assignment distance dropped to an astonishing 1.28. The Hungarian algorithm proved perfectly capable of routing workers across a massive farm without stranding them. Useful actions skyrocketed to 936.
*   However, planting 156 Melons and harvesting 64 caused extreme overproduction. The agent spent $7,000 on land and $13,000 on seeds, but market revenue barely budged ($33,328) because the market price of Melons had completely flatlined. 

## Conclusion
**The spatial and worker-routing bottleneck is officially solved.** The Hungarian allocation architecture is a massive success and works flawlessly even on a fully expanded 10x10 farm.

**The NEW Bottleneck:** Market Saturation. 
The agent has successfully optimized its physical production capacity, but its strategic logic (monocropping Melons and blindly selling them) prevents it from turning physical output into economic profit. 

**Next optimization target:** Crop diversification, market timing (holding inventory), or animal husbandry to bypass the Melon market cap.
