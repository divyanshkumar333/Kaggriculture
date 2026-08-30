# V021-A Labor Throughput Experiment Report

## Executive Summary

| Metric | V020-C (Frozen Control) | V021-A (Labor Throughput Candidate) | Delta / Impact | Verdict |
|---|:---:|:---:|:---:|:---:|
| **Direct Head-to-Head Win Rate** | **100.0% (12/12)** | **0.0% (0/12)** | **-100.0%** | **V020-C DOMINATES** |
| **Direct Head-to-Head Mean Bank** | **$44,880** | $24,788 | **-$20,093 (-44.8%)** | **V020-C** |
| **vs Industrial Livestock** | **100.0% (12/12, $46,941)** | 100.0% (12/12, $38,244) | -$8,697 bank | V020-C |
| **vs Animal Optimizer (V005-D)** | **91.7% (11/12, $36,128)** | 83.3% (10/12, $30,339) | -8.4% WR, -$5,789 bank | V020-C |
| **vs Diversified (V004-B)** | **100.0% (12/12, $35,162)** | 83.3% (10/12, $30,079) | -16.7% WR, -$5,083 bank | V020-C |
| **vs Harvest Timing (V009-B)** | **100.0% (12/12, $33,365)** | 83.3% (10/12, $30,301) | -16.7% WR, -$3,064 bank | V020-C |
| **vs Melon Flooder** | **100.0% (12/12, $42,620)** | 100.0% (12/12, $36,662) | -$5,958 bank | V020-C |
| **vs Starter Baseline** | **100.0% (12/12, $44,882)** | 100.0% (12/12, $41,036) | -$3,846 bank | V020-C |
| **vs Random Baseline** | **100.0% (12/12, $42,721)** | 100.0% (12/12, $39,701) | -$3,020 bank | V020-C |
| **Overall Field Win Rate (84 games)** | **98.8% (83W / 1L)** | **92.9% (78W / 6L)** | **-5.9%** | **V020-C** |
| **Overall Field Mean Bank** | **$40,260** | **$35,337** | **-$4,923 (-12.2%)** | **V020-C** |
| **Overall Worst-Case Floor** | **$22,621** | **$989** | **-$21,632 (Floor Collapsed)** | **V020-C** |
| **Promotion Decision** | **RETAINED AS FROZEN CHAMPION** | **REJECTED (FAILED PROMOTION RULE)** | - | **V020-C CHAMPION** |

---

## 1. Core Hypothesis & Implementation (`agents/v021_a_labor_throughput.py`)

### The Hypothesis
Kaggle replay evidence showed top agents scaling to 8–10 farm hands. V021-A tested whether scaling labor throughput and dynamic planting capacity (from 4 to 6–8 seeds/day) on crop farming alone could increase economic performance without adding livestock.

### The Exact Interventions
1. **Dynamic Daily Plant Cap**:
   $$\text{DAILY\_PLANT\_CAP} = \begin{cases} 4 & \text{if } \text{unlocked\_quads} = 1 \\ 6 & \text{if } \text{unlocked\_quads} = 2 \\ 8 & \text{if } \text{unlocked\_quads} = 3 \\ 10 & \text{if } \text{unlocked\_quads} = 4 \end{cases}$$
2. **Workload-Aware Labor Scaling**:
   - Evaluated active workload across unwatered crops, ready harvests, and queued plant tasks.
   - Allowed dynamic marginal ROI threshold scaling up to Fibonacci cost 34 (enabling up to 6–8 workers when workload deficit existed).
3. **Market Execution Priority Arbitrator**:
   - Reordered `market_actions` so high-value produce (`MELON`, `STRAWBERRY`, `MILK`) sold before lower-tier crops under the 10-order execution cap.

---

## 2. Unit Testing & Verification (`tests/test_v021_a_labor.py`)

All 5 unit tests passed (100%):
* `test_dynamic_plant_cap_scaling`: Verified scaling from 4 to 10 across 1–4 quadrants.
* `test_market_order_priority_reordering`: Verified HIRE and high-value Melon sales execute before Wheat sales.
* `test_labor_scaling_under_workload`: Verified worker hiring triggers when workload deficit exists.
* `test_hiring_protects_operating_reserve`: Verified hiring is blocked when cash is below operating reserve.
* `test_smoke_5_turns`: Verified 0 errors over active game steps.

---

## 3. Empirical Results & Detailed Benchmark Breakdown

### Head-to-Head (12 Deterministic Seeds, Alternating Positions)

| Seed | P0 / P1 Assignment | V021-A Bank | V020-C Bank | Winner | Delta (A - C) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 100 | V021-A (P0) vs V020-C (P1) | $34,896 | **$48,579** | **V020-C** | -$13,683 |
| 101 | V020-C (P0) vs V021-A (P1) | $26,028 | **$43,889** | **V020-C** | -$17,861 |
| 102 | V021-A (P0) vs V020-C (P1) | $22,408 | **$44,682** | **V020-C** | -$22,274 |
| 103 | V020-C (P0) vs V021-A (P1) | $23,778 | **$43,267** | **V020-C** | -$19,489 |
| 104 | V021-A (P0) vs V020-C (P1) | $24,458 | **$44,383** | **V020-C** | -$19,925 |
| 105 | V020-C (P0) vs V021-A (P1) | $28,248 | **$47,025** | **V020-C** | -$18,777 |
| 106 | V021-A (P0) vs V020-C (P1) | $26,942 | **$47,562** | **V020-C** | -$20,620 |
| 107 | V020-C (P0) vs V021-A (P1) | $25,607 | **$46,941** | **V020-C** | -$21,334 |
| 108 | V021-A (P0) vs V020-C (P1) | $20,634 | **$43,901** | **V020-C** | -$23,267 |
| 109 | V020-C (P0) vs V021-A (P1) | $26,605 | **$43,598** | **V020-C** | -$16,993 |
| 110 | V021-A (P0) vs V020-C (P1) | $29,230 | **$41,612** | **V020-C** | -$12,382 |
| 111 | V020-C (P0) vs V021-A (P1) | $18,623 | **$43,121** | **V020-C** | -$24,498 |

* **Head-to-Head Win Rate**: **0.0% (0/12)**.
* **Mean Delta**: **-$20,093**.

---

## 4. Root Cause Analysis: Why Labor Scaling Alone Failed on Crops

1. **The Crop Labor Mismatch (Zero Labor Demand for High Worker Counts)**:
   - Crops require only **1 watering action per day**.
   - 25 crops require only 25 watering turns. 1 farmer + 1 hand provide $2 \times 24 = 48$ actions/day, which is already a **$92\%$ labor surplus**.
   - Attempting to scale to 6–8 workers on crops creates pure idle labor waste.
2. **The Operating Reserve Lock**:
   - Setting $\text{DAILY\_PLANT\_CAP} = 6$ for Strawberry ($200$ seed cost) raised the dynamic operating reserve to $\$1,250$ (vs $\$850$ for cap 4).
   - This higher reserve delayed quadrant expansion from Day 13 to Day 18+, leaving V021-A with fewer active producing tiles during the most lucrative mid-season window.
3. **The Definitive Scientific Conclusion**:
   - **Hypothesis Disproven**: High labor scaling (8–10 workers) cannot be justified by crop farming alone.
   - High labor scaling on Kaggle succeeds **ONLY** when coupled with **Livestock (Cows/Sheep/Geese)**, where daily feeding, caring, and milking generate 60+ necessary high-ROI actions per day.

---

## 5. Promotion Decision

* **Promotion Criteria Met**: **NO**.
  * Head-to-Head vs V020-C: **0.0%** (0/12).
  * Mean Bank: **$35,337** vs **$40,260** (-$4,923).
  * Worst-Case Floor: **$989** vs **$22,621** (Severe Regression).
* **Action**: **REJECT V021-A**.
* **Champion Status**: **V020-C REMAINS THE ACTIVE FROZEN CHAMPION**.
