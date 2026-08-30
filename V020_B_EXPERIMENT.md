# V020-B Competitive Adaptive Experiment Report

## Executive Summary

| Metric | V020-A Control (V018-B Champion) | V020-B (Simplified Adaptive) | Status / Winner |
|---|---|---|---|
| **Direct Head-to-Head Win Rate** | **100.0% (12W / 0L / 0T)** | **0.0% (0W / 12L / 0T)** | **V020-A WINS** |
| **Direct Head-to-Head Mean Bank** | **$44,074** | $1,346 | **V020-A +$42,728** |
| **Overall Field Win Rate (108 games)** | **70.0% (76W / 30L / 2T)** | **44.4% (48W / 60L / 0T)** | **V020-A (+25.6%)** |
| **Field Mean Bank** | **$31,830** | $13,420 | **V020-A +$18,410** |
| **Field Worst-Case Bank** | **$3,319** | $798 | **V020-A** |
| **Promotion Decision** | **RETAINED AS CHAMPION** | **REJECTED** | **V020-A REMAINED** |

---

## 1. Experimental Objective & Hypothesis

### Objective:
Address V020-A's vulnerability against historical active opponents (Animals V005-D, Harvest Timing V009-B, Diversified V004-B) by implementing:
1. Strict crop lifecycle filtering (Melon $\le$ Day 18, Carrot $\le$ Day 25, Wheat $\le$ Day 27).
2. Fractional seed stall prevention.
3. Lower land expansion reserve ($+\$800$ instead of $+\$2,500$).
4. Endgame harvesting and liquidation freeze on Days 28–29.

### Implementation:
`agents/v020_b_competitive_adaptive.py` with standalone unit tests in `tests/test_v020_competitive_adaptive.py`.

---

## 2. Empirical Benchmark Matrix (12 Seeds per Opponent)

| Opponent Archetype | V020-A Control Win Rate | V020-A Mean Bank | V020-B Win Rate | V020-B Mean Bank |
|---|:---:|:---:|:---:|:---:|
| **vs V020-A Control** | 41.7% (Self-play) | $20,324 | **0.0%** | $1,346 |
| **vs Animal (V005-D)** | **25.0%** | $18,479 | **0.0%** | $6,476 |
| **vs Harvest Timing (V009-B)** | **33.3%** | $19,225 | **0.0%** | $2,574 |
| **vs Diversified (V004-B)** | **41.7%** | $18,536 | **0.0%** | $9,571 |
| **vs Dynamic Clusters (V008-D)**| **58.3%** | $25,145 | **0.0%** | $7,159 |
| **vs Melon Flooder** | **100.0%** | $37,763 | **100.0%** | $17,629 |
| **vs Balanced Optimizer** | **100.0%** | $44,294 | **100.0%** | $22,329 |
| **vs Starter** | **100.0%** | $44,429 | **100.0%** | $26,685 |
| **vs Random** | **100.0%** | $45,801 | **100.0%** | $27,008 |
| **OVERALL** | **70.0%** | **$31,830** | **44.4%** | **$13,420** |

---

## 3. Root Cause Analysis of V020-B Failure

1. **Over-simplification of Worker Routing & Clustering**:
   - V018-B / V020-A utilizes a highly calibrated spatial clustering heuristic that pairs worker labor capacity with physical Euclidean crop clusters to minimize travel turns.
   - V020-B replaced this with naive greedy closest-tile matching, resulting in massive worker travel thrashing and missed watering cycles.
2. **Key Takeaway for V020-C**:
   - **Never rewrite core modules.**
   - All subsequent experiments must use `agents/v020_a_control.py` as the direct codebase and make **surgical $\le 5$-line diffs** directly on the working champion code.

---

## 4. Promotion Ruling

Under the strict promotion criteria:
* V020-B lost 100% of matches to V020-A Control (0W / 12L).
* V020-B decreased field win rate by 25.6% and average bank by $18.4k.
* **V020-B is REJECTED. V020-A remains the undisputed champion.**
