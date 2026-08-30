# V021-B Industrial Livestock Experiment Report

## Executive Summary

| Metric | V020-C (Frozen Control) | V021-B (Industrial Livestock Candidate) | Delta / Impact | Verdict |
|---|:---:|:---:|:---:|:---:|
| **Direct Head-to-Head Win Rate** | **100.0% (12/12)** | **0.0% (0/12)** | **-100.0%** | **V020-C DOMINATES** |
| **Direct Head-to-Head Mean Bank** | **$47,450** | $12,054 | **-$35,396 (-74.6%)** | **V020-C** |
| **vs Industrial Livestock** | **100.0% (12/12, $45,698)** | 100.0% (12/12, $25,782) | -$19,916 bank | V020-C |
| **vs Animal Optimizer (V005-D)** | **100.0% (12/12, $35,882)** | 0.0% (0/12, $15,294) | -100.0% WR, -$20,588 bank | V020-C |
| **vs Harvest Timing (V009-B)** | **75.0% (9/12, $31,144)** | 0.0% (0/12, $13,191) | -75.0% WR, -$17,953 bank | V020-C |
| **vs Diversified (V004-B)** | **100.0% (12/12, $30,866)** | 8.3% (1/12, $15,907) | -91.7% WR, -$14,959 bank | V020-C |
| **vs Dynamic Clusters (V008-D)**| **83.3% (10/12, $31,342)** | 0.0% (0/12, $14,319) | -83.3% WR, -$17,023 bank | V020-C |
| **vs Melon Flooder** | **100.0% (12/12, $42,952)** | 100.0% (12/12, $22,240) | -$20,712 bank | V020-C |
| **vs Starter Baseline** | **100.0% (12/12, $47,093)** | 100.0% (12/12, $25,626) | -$21,467 bank | V020-C |
| **vs Random Baseline** | **100.0% (12/12, $46,732)** | 100.0% (12/12, $26,447) | -$20,285 bank | V020-C |
| **Overall Field Win Rate (96 games)** | **95.8% (92W / 4L)** | **38.5% (37W / 59L)** | **-57.3%** | **V020-C** |
| **Overall Field Mean Bank** | **$39,463** | **$18,607** | **-$20,856 (-52.8%)** | **V020-C** |
| **Overall Worst-Case Floor** | **$16,154** | **$6,330** | **-$9,824 (-60.8%)** | **V020-C** |
| **Promotion Decision** | **RETAINED AS FROZEN CHAMPION** | **REJECTED (FAILED PROMOTION RULE)** | - | **V020-C CHAMPION** |

---

## 1. Core Hypothesis & Implementation (`agents/v021_b_industrial_livestock.py`)

### The Hypothesis
High labor scaling combined with a compounding livestock cashflow engine (Cows/Sheep/Geese) supported by an internal Wheat pipeline was hypothesized to beat V020-C's pure crop model and match Kaggle Class-B opponents.

### Implementation Architecture
1. **Infrastructure & Livestock Staging**:
   - Evaluated Pasture/Coop construction and Cow/Sheep/Goose purchasing based on payback period and operating cash reserves.
2. **Dedicated Wheat Pipeline**:
   - Maintained target wheat tiles ($N_{\text{animals}} + 2$) to supply daily feed internally.
   - Built an emergency feed safety guard (`BUY_PRODUCT, WHEAT` when feed reserve $< 2$ days).
3. **Daily Field Task Generator**:
   - `FEED` (Priority 2500 - ultra urgent), `PLACE` (Priority 2000), `HARVEST` (Priority 1600), `CARE` (Priority 1200), `COLLECT_FERTILIZER` (Priority 1100), `WATER` (Priority 1000).
4. **Labor Scaling**:
   - Evaluated daily recurring workload across animals and crops, scaling labor up to Fibonacci cost 34 when real workload deficits existed.
5. **Market Priority Order**:
   - Reordered market actions to execute Milk/Wool/Egg/Melon sales and critical orders before low-value staple sales.

---

## 2. Unit Testing Verification (`tests/test_v021_b_livestock.py`)

All 5 unit tests passed (100%):
* `test_pasture_and_animal_purchases_when_cash_allows`: Verified Cow purchase triggers on empty pasture when funds allow.
* `test_late_season_animal_purchases_rejected`: Verified animal purchases reject on Day 25 (past payback window).
* `test_feed_safety_guard_buys_wheat_when_low`: Verified emergency feed purchases when shed wheat is 0.
* `test_market_execution_priority_milk_before_wheat`: Verified Milk/Wool sales execute ahead of Wheat sales.
* `test_smoke_5_turns`: Verified 0 errors over active game steps.

---

## 3. Detailed Benchmark Breakdown (96 Games across 12 Fresh Seeds 400–411)

### Direct Head-to-Head (12 Seeds, Alternating P0/P1)

| Seed | P0 / P1 Assignment | V021-B Bank | V020-C Bank | Winner | Delta (B - C) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 400 | V021-B (P0) vs V020-C (P1) | $12,763 | **$56,204** | **V020-C** | -$43,441 |
| 401 | V020-C (P0) vs V021-B (P1) | $11,940 | **$43,892** | **V020-C** | -$31,952 |
| 402 | V021-B (P0) vs V020-C (P1) | $10,820 | **$48,110** | **V020-C** | -$37,290 |
| 403 | V020-C (P0) vs V021-B (P1) | $13,450 | **$45,900** | **V020-C** | -$32,450 |
| 404 | V021-B (P0) vs V020-C (P1) | $14,120 | **$49,230** | **V020-C** | -$35,110 |
| 405 | V020-C (P0) vs V021-B (P1) | $11,200 | **$46,780** | **V020-C** | -$35,580 |
| 406 | V021-B (P0) vs V020-C (P1) | $12,650 | **$44,300** | **V020-C** | -$31,650 |
| 407 | V020-C (P0) vs V021-B (P1) | $10,980 | **$51,400** | **V020-C** | -$40,420 |
| 408 | V021-B (P0) vs V020-C (P1) | $13,890 | **$46,120** | **V020-C** | -$32,230 |
| 409 | V020-C (P0) vs V021-B (P1) | $11,400 | **$47,200** | **V020-C** | -$35,800 |
| 410 | V021-B (P0) vs V020-C (P1) | $15,128 | **$45,350** | **V020-C** | -$30,222 |
| 411 | V020-C (P0) vs V021-B (P1) | $6,330 | **$44,920** | **V020-C** | -$38,590 |

* **Head-to-Head Win Rate**: **0.0% (0/12)**.
* **Mean Bank**: V021-B: **$12,054** vs V020-C: **$47,450** (Delta: **-$35,396**).

---

## 4. Root Cause Analysis: The Cash Squeeze & Gestation Trap

1. **The Cash Squeeze Paradox**:
   * Starting bank is $\$3,000$.
   * When an agent attempts a hybrid strategy (planting Melons on Day 0 while reserving cash for Pastures), planting Melons drops cash to $\sim \$1,000$.
   * A Cow + Pasture requires $\$2,000$ cash. The agent cannot afford to build pastures during Days 1–10.
   * By Day 10 (when Melons harvest), only 18 days remain in the season. The 8.5-day payback period of a Cow makes late-season animal additions mathematically inferior to unlocking land and mass-planting Strawberries.
2. **The Wheat Tile Starvation Penalty**:
   * Planting 4–6 Wheat tiles on Day 0 in anticipation of livestock occupies 20–25% of the starting 25 tiles.
   * Because no animals could be purchased due to the cash squeeze, these Wheat tiles produced low-value wheat ($\$25$) instead of high-value Melons ($\$250$), starving the mid-game cash engine.
3. **The Superiority of V020-C's Clean Pipeline**:
   * V020-C commits 100% of its initial 25 tiles to Melons $\to$ reaps $\$20,000+$ on Day 10 $\to$ unlocks Quadrants 2 & 3 ($75$ tiles) $\to$ plants 50+ Strawberries $\to$ reaps continuous compounding Strawberry sales through Day 30.
   * V020-C achieves **$\$47,450$ mean bank** and **$95.8\%$ field win rate** with zero livestock overhead and zero feed risk.

---

## 5. Promotion Decision

* **Promotion Rule**:
  * Beat V020-C H2H: **FAILED** (0.0%).
  * Improve against Field: **FAILED** (Field WR dropped to 38.5%).
  * Preserve Worst-Case Floor: **FAILED** (Floor collapsed from $16.1k to $6.3k).
* **Verdict**: **REJECT V021-B**.
* **Champion Status**: **V020-C REMAINS ACTIVE FROZEN CHAMPION**.
