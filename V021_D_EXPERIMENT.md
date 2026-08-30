# V021-D Economically Gated Throughput Scaling Experiment Report

## Executive Summary

| Metric | V020-C (Frozen Control) | V021-D (Throughput Candidate) | Delta / Impact | Verdict |
|---|:---:|:---:|:---:|:---:|
| **Direct Head-to-Head Win Rate (20 Fresh Seeds)** | **100.0% (20/20)** | **0.0% (0/20)** | **-100.0%** | **V020-C DOMINATES** |
| **Direct Head-to-Head Mean Bank** | **$39,503** | $26,019 | **-$13,484 (-34.1%)** | **V020-C** |
| **vs Industrial Livestock** | **100.0% (12/12, $56,530)** | 100.0% (12/12, $36,144) | -$20,386 bank | V020-C |
| **vs Animal Optimizer (V005-D)** | 83.3% (10/12, $31,180) | **100.0% (12/12, $26,366)** | +16.7% WR, -$4,814 bank | Mixed |
| **vs Harvest Timing (V009-B)** | **100.0% (12/12, $36,297)** | 33.3% (4/12, $24,832) | -66.7% WR, -$11,465 bank | V020-C |
| **vs Diversified (V004-B)** | **100.0% (12/12, $35,059)** | 91.7% (11/12, $28,037) | -8.3% WR, -$7,022 bank | V020-C |
| **vs Dynamic Clusters (V008-D)**| **100.0% (12/12, $35,863)** | 66.7% (8/12, $24,707) | -33.3% WR, -$11,156 bank | V020-C |
| **vs Melon Flooder** | **100.0% (12/12, $43,280)** | 100.0% (12/12, $31,394) | -$11,886 bank | V020-C |
| **vs Starter Baseline** | **100.0% (12/12, $47,580)** | 100.0% (12/12, $35,774) | -$11,806 bank | V020-C |
| **vs Random Baseline** | **100.0% (12/12, $46,938)** | 100.0% (12/12, $36,369) | -$10,569 bank | V020-C |
| **Overall Field Win Rate (96 games)** | **97.9% (94W / 2L)** | **86.5% (83W / 13L)** | **-11.4%** | **V020-C** |
| **Overall Field Mean Bank** | **$41,591** | **$29,353** | **-$12,238 (-29.4%)** | **V020-C** |
| **Overall Worst-Case Floor** | $16,901 | **$17,729** | +$828 (Safe floor) | V021-D |
| **Promotion Decision** | **RETAINED AS FROZEN CHAMPION** | **REJECTED (FAILED PROMOTION RULE)** | - | **V020-C CHAMPION** |

---

## 1. Profiling Findings on Frozen Champion (V020-C)

We executed an exhaustive day-by-day telemetry profile across 12 deterministic seeds:

1. **Stage 1 (Days 0–10)**:
   - Planted 21.9 Melons on 25 unlocked tiles with 1 hand (48 actions/day).
   - 0 unwatered crop deaths, 0 misses, 100% capacity utilization.
2. **Stage 2 (Days 11–30)**:
   - Melon sales generated $\$15,000\text{--}\$23,000$ cash on Days 11–13.
   - Land expanded to 50 tiles (Day 12) and 75 tiles (Day 15).
   - **The Real Scaling Bottleneck**: Strawberries plateaued at **46.2 active plants** because 1 farmer + 1 hand (48 total daily turns) could not physically water and harvest more than 46 crops.

---

## 2. What Was Tested in V021-D

1. **Dynamic Plant Cap Scaling**:
   - `DAILY_PLANT_CAP = 4` during Stage 1 (Days 0–10).
   - Scaled to 6–10 seeds/day in Stage 2 (Day 11+) once liquidity exceeded $\$4,000\text{--}\$12,000$.
2. **Workload-Matched Labor**:
   - Targeted 2–3 hands when active crops exceeded 48–68 tiles.
3. **Economically Gated Land Expansion**:
   - Only purchased land when existing quadrant was filled ($\le 5$ empty tiles) and cash was protected.

---

## 3. Detailed Benchmark Breakdown

### Head-to-Head (20 Fresh Seeds 700–719, Alternating P0/P1)

| Seeds 700–719 (20 Games) | V021-D | V020-C | Outcome |
|---|:---:|:---:|:---:|
| **Win / Loss / Tie** | 0W | **20W** | **V020-C (100.0%)** |
| **Mean Bank** | $26,019 | **$39,503** | **-$13,484** |
| **Median Bank** | $26,350 | **$39,120** | **-$12,770** |
| **Worst-Case Bank** | $16,493 | **$29,812** | **-$13,319** |

---

## 4. Root Cause Analysis: The Premature Land Trap on Day 2

Frame-by-frame tracing of Seed 700 revealed why V021-D underperformed:
1. **The Day-2 Land Purchase**:
   - In V021-D, setting `operating_reserve = cash_reserve + (DAILY_PLANT_CAP * 80) = $370` allowed the agent to buy Quadrant 2 on **Day 2** ($1500 > $1000 + $370).
   - Spending $\$1,000$ on Day 2 depleted working capital down to $\$394$, starving the agent during the crucial Day 3–10 Melon growth cycle.
2. **The Contrast with V020-C**:
   - In V020-C, the static land operating reserve ($\$720$) blocked land expansion on Day 2, preserving $\$980+$ working cash.
   - V020-C only expanded land on Day 12 when it had **$\$15,000+$ in cash**, allowing it to buy Quadrants 2 & 3 without ever endangering its cash flow.

---

## 5. Promotion Decision

* **Promotion Rule**:
  * Direct H2H vs V020-C: **FAILED** (0.0% Win Rate, 0/20).
  * Field Performance: Mean bank dropped from $\$41,591$ to $\$29,353$.
* **Verdict**: **REJECT V021-D**.
* **Champion Status**: **V020-C REMAINS ACTIVE FROZEN CHAMPION**.
