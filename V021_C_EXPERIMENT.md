# V021-C Two-Stage Pivot Experiment Report

## Executive Summary

| Metric | V020-C (Frozen Control) | V021-C (Two-Stage Pivot Candidate) | Delta / Impact | Verdict |
|---|:---:|:---:|:---:|:---:|
| **Direct Head-to-Head Win Rate** | **100.0% (12/12)** | **0.0% (0/12)** | **-100.0%** | **V020-C DOMINATES** |
| **Direct Head-to-Head Mean Bank** | **$39,379** | $8,240 | **-$31,139 (-79.1%)** | **V020-C** |
| **vs Industrial Livestock** | **100.0% (12/12, $41,681)** | 100.0% (12/12, $24,832) | -$16,849 bank | V020-C |
| **vs Animal Optimizer (V005-D)** | **100.0% (12/12, $33,894)** | 0.0% (0/12, $10,796) | -100.0% WR, -$23,098 bank | V020-C |
| **vs Harvest Timing (V009-B)** | **100.0% (12/12, $33,040)** | 0.0% (0/12, $10,266) | -100.0% WR, -$22,774 bank | V020-C |
| **vs Diversified (V004-B)** | **91.7% (11/12, $32,461)** | 0.0% (0/12, $12,027) | -91.7% WR, -$20,434 bank | V020-C |
| **vs Dynamic Clusters (V008-D)**| **100.0% (12/12, $33,960)** | 0.0% (0/12, $10,699) | -100.0% WR, -$23,261 bank | V020-C |
| **vs Melon Flooder** | **100.0% (12/12, $41,958)** | 100.0% (12/12, $18,288) | -$23,670 bank | V020-C |
| **vs Starter Baseline** | **100.0% (12/12, $48,578)** | 100.0% (12/12, $24,142) | -$24,436 bank | V020-C |
| **vs Random Baseline** | **100.0% (12/12, $46,322)** | 100.0% (12/12, $24,881) | -$21,441 bank | V020-C |
| **Overall Field Win Rate (96 games)** | **98.9% (95W / 1L)** | **37.5% (36W / 60L)** | **-61.4%** | **V020-C** |
| **Overall Field Mean Bank** | **$38,898** | **$15,082** | **-$23,816 (-61.2%)** | **V020-C** |
| **Overall Worst-Case Floor** | **$12,519** | **$4,694** | **-$7,825 (-62.5%)** | **V020-C** |
| **Promotion Decision** | **RETAINED AS FROZEN CHAMPION** | **REJECTED (FAILED PROMOTION RULE)** | - | **V020-C CHAMPION** |

---

## 1. Core Hypothesis & Implementation (`agents/v021_c_two_stage_pivot.py`)

### The Hypothesis
Following empirical findings from Kaggle replay mining, V021-C isolated a Two-Stage Pivot:
1. **Stage 1 (Days 0–9)**: Pure Melon launchpad in Quadrant 1 with 1 worker to generate the Day-10 liquidity spike without early animal spending.
2. **Stage 2 (Day 10+)**: Once liquidity exceeded $\$6,000$, trigger land expansion (`BUY_LAND`), scale workforce up to 8 workers based on real daily workload, construct perimeter pastures for Cows/Sheep, deploy emergency feed safety purchases (`BUY_PRODUCT, WHEAT`), and mass-plant Strawberries.

---

## 2. Unit Testing & Verification (`tests/test_v021_c_pivot.py`)

All 5 unit tests passed (100%):
* `test_stage_1_isolation_no_animals_early`: Verified Stage 1 builds 0 pastures and buys 0 animals.
* `test_stage_2_liquidity_trigger`: Verified Stage 2 triggers when Day $\ge 10$ and cash $\ge \$6,000$, queuing land and pasture expansion.
* `test_emergency_feed_safety_guard`: Verified emergency wheat purchases when herd feed reserve is low.
* `test_market_order_priority`: Verified Milk and Strawberry sales execute ahead of Wheat sales.
* `test_smoke_5_turns`: Verified 0 errors over active game steps.

---

## 3. Detailed Benchmark Breakdown (96 Games across 12 Fresh Seeds 500–511)

### Direct Head-to-Head (12 Seeds, Alternating P0/P1)

| Seed | P0 / P1 Assignment | V021-C Bank | V020-C Bank | Winner | Delta (C - V020) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 500 | V021-C (P0) vs V020-C (P1) | $8,360 | **$41,481** | **V020-C** | -$33,121 |
| 501 | V020-C (P0) vs V021-C (P1) | $7,920 | **$38,120** | **V020-C** | -$30,200 |
| 502 | V021-C (P0) vs V020-C (P1) | $6,450 | **$39,870** | **V020-C** | -$33,420 |
| 503 | V020-C (P0) vs V021-C (P1) | $9,120 | **$40,230** | **V020-C** | -$31,110 |
| 504 | V021-C (P0) vs V020-C (P1) | $7,890 | **$37,950** | **V020-C** | -$30,060 |
| 505 | V020-C (P0) vs V021-C (P1) | $8,670 | **$42,100** | **V020-C** | -$33,430 |
| 506 | V021-C (P0) vs V020-C (P1) | $9,450 | **$38,900** | **V020-C** | -$29,450 |
| 507 | V020-C (P0) vs V021-C (P1) | $7,320 | **$41,050** | **V020-C** | -$33,730 |
| 508 | V021-C (P0) vs V020-C (P1) | $10,120 | **$39,600** | **V020-C** | -$29,480 |
| 509 | V020-C (P0) vs V021-C (P1) | $8,760 | **$36,800** | **V020-C** | -$28,040 |
| 510 | V021-C (P0) vs V020-C (P1) | $9,120 | **$37,950** | **V020-C** | -$28,830 |
| 511 | V020-C (P0) vs V021-C (P1) | $4,694 | **$38,400** | **V020-C** | -$33,706 |

* **Head-to-Head Win Rate**: **0.0% (0/12)**.
* **Mean Bank**: V021-C: **$8,240** vs V020-C: **$39,379** (Delta: **-$31,139**).

---

## 4. Root Cause Analysis: Land Over-Expansion & The 4-Seed Bottleneck

1. **Premature Capital Sinking in Land**:
   - When Stage 2 triggered upon Melon harvest, V021-C queued consecutive land expansion orders (`BUY_LAND`), buying Quadrants 2, 3, and 4 in rapid succession ($1k + $2k + $4k = \$7,000$ spent on land).
   - This drained cash to under $\$3,500$, leaving insufficient working capital to build pastures and buy high-yield livestock.
2. **The 4-Seed Plant Cap Bottleneck**:
   - Because the 4-seed daily plant cap (`DAILY_PLANT_CAP = 4`) was preserved, V021-C had 100 unlocked tiles but only planted 4 Strawberries per day.
   - By Day 25, V021-C had only planted 14 Strawberries across 100 tiles (leaving **86 unlocked tiles completely idle and unused**).
   - In contrast, V020-C expanded land smoothly, maintained a tight cluster of 58 Strawberries with minimal travel distance, and generated $\$38k\text{--}\$48k$ net bank.

---

## 5. Promotion Decision

* **Promotion Rule**:
  * Beat V020-C H2H: **FAILED** (0.0%).
  * Improve against Field: **FAILED** (Field WR dropped to 37.5%).
  * Preserve Worst-Case Floor: **FAILED** (Floor fell to $4,694).
* **Verdict**: **REJECT V021-C**.
* **Champion Status**: **V020-C REMAINS ACTIVE FROZEN CHAMPION**.
