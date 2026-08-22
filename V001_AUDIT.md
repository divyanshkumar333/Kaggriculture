# v001 Baseline Audit

This document evaluates the `v001_baseline.py` implementation against the actual Kaggriculture mechanics to identify gaps, stubs, and major bottlenecks before optimization.

| Component | Implemented | Actually Used | Correct | Tested | Major Issues |
| --------- | ----------- | ------------- | ------- | ------ | ------------ |
| **State Parser** | Yes | Yes | Yes | Pending | Simplistic; doesn't track town shop demand exactly. |
| **Movement/Pathfinding** | Partial | Yes | Yes | Pending | Greedy single-axis step (e.g. always moves West before North). Not true BFS/A*. |
| **Planting** | Yes | Yes | Yes | Pending | Only plants Melons. |
| **Watering** | Yes | Yes | Yes | Pending | Working correctly for planted crops. |
| **Harvesting** | Yes | Yes | Yes | Pending | Working correctly for mature crops. |
| **Animal Management** | Stub | No | No | No | `FEED` is scheduled, but `BUILD_COOP`, `PLACE`, `CARE`, `COLLECT_FERTILIZER` are missing. Animals are never purchased. |
| **Fertilizer Logic** | Stub | No | No | No | Not implemented. |
| **Hiring (Marginal ROI)** | Yes | Yes | No | Pending | Evaluates ROI and issues `HIRE`. **CRITICAL FLAW:** `ActionExecutor` forces all hired hands to `["PASS"]`. Hires waste money. |
| **Land Expansion** | Stub | No | No | No | Not implemented. |
| **Market Selling** | Yes | Yes | Yes | Pending | Trickle-sells up to 2 units if price > 50. Basic, but functional. |
| **Price Impact Model** | Stub | Yes | No | Pending | Uses a naive 1% drop-per-unit heuristic instead of the exact hinge/sqrt/log curves from the environment. |
| **Cash Reserve** | Yes | Yes | Yes | Pending | A hard-coded reserve of 50 is used to prevent over-spending on seeds/hiring. |
| **Daily Scheduling** | Yes | Yes | Yes | Pending | Prioritizes Watering/Feeding (10) over Harvesting (20) over Planting (30). |

## Critical Bottlenecks to Fix Before Benchmarking

1. **Idle Farm Hands:** The agent pays for farm hands but does not assign them tasks. This guarantees economic ruin.
2. **Missing Economic Math:** The `EconomicCalculator` uses fake heuristics instead of the real Kaggle formulas for price impact.
3. **Animal & Fertilizer Void:** The entire animal synergy system is missing.

## Recommendations for Next Steps (Phase 6-12)

Before running the extensive Benchmark Suite, we must implement:
1. **True Task Allocation:** Ensure hired hands execute tasks.
2. **Accurate Math:** Update `EconomicCalculator` to use the actual `kaggriculture` price curve logic.
3. **True Pathfinding:** Implement BFS/A* to minimize movement turns.
