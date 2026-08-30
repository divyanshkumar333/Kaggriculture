# V020 Competitive Roadmap & Strategy Guide

## Current Rating & Milestones

| Target Tier | Rating Range | Primary Objective | Current Status |
|---|---|---|---|
| **Baseline Submission** | **600.0** | Establish Official Benchmark with V018-B Champion | **ACTIVE (Official Score: 600.0)** |
| **Phase 1 Target** | **1000.0** | Robustness against active/adversarial human strategies | **V020-C READY FOR REVIEW** |
| **Phase 2 Target** | **1500.0** | Advanced multi-quadrant land expansion & animal balance | Queued |
| **Phase 3 Target** | **2000.0** | Dynamic market exploitation & counter-strategies | Queued |
| **Phase 4 Target** | **2500.0** | High-precision spatial routing & micro-efficiency | Queued |
| **Phase 5 Target** | **3000.0** | Global Leaderboard Dominance | Long-term Goal |

---

## Current Status & Champion Integrity

* **Submitted Baseline**: `main.py` (`agents/v018_b_batch_cap.py` / `agents/v020_a_control.py`)
* **SHA-256 Hash**: `8E802A6BF8263D191C55D78C5EA9E6D43AD27F734CB592228EBA0BA6A0158733`
* **Status**: **UNMODIFIED SUBMISSION COPY**

---

## 1. Candidate History & Evaluation Ledger

### V019-B (Market-Adaptive Dynamic Evaluator)
* **Hypothesis**: Switch from Melon to Wheat when Melon market drops.
* **Result**: **REJECTED**. Lost 75% of H2H matches vs Control because Melon recovered via town shops ($30–$50/melon) while Wheat remained capped at $25.

### V020-B (Simplified Adaptive Architecture)
* **Hypothesis**: Architectural rewrite with lifecycle filtering, seed stall fix, and lower land reserve.
* **Result**: **REJECTED**. Lost 100% of H2H matches vs Control (Win rate 44.4%, bank $13,420) due to degradation of Hungarian spatial clustering heuristics.

### V020-C (Surgical Competitive Optimization)
* **Hypothesis**: Surgical 18-line diff on V020-A Control fixing fractional seed stall, lifecycle guard, and dynamic land expansion reserve.
* **Empirical Result**: **PROMOTED AS CHAMPION CANDIDATE**.
  * **Head-to-Head vs V020-A Control**: **100.0% Win Rate (12W / 0L / 0T)** | Bank: **$32,950** vs **$14,798**
  * **Overall Field Win Rate (108 games)**: **99.1% (107W / 1L / 0T)** (up from 70.0%)
  * **Worst-Case Floor**: **$20,634** (up from $3,319 — **6.2x improvement**)
  * **vs Animals (V005-D)**: **100.0%** (up from 25.0%)
  * **vs Harvest Timing (V009-B)**: **91.7%** (up from 33.3%)
  * **vs Diversified (V004-B)**: **100.0%** (up from 41.7%)

---

## 2. Summary Scorecard: V020-A vs V020-C

| Opponent Archetype | V020-A Control Win Rate | V020-C Surgical Win Rate | V020-C Delta |
|---|:---:|:---:|:---:|
| **vs V020-A Control** | 41.7% (Self-play) | **100.0% (12/12)** | **+58.3%** |
| **vs Animal Optimizer (V005-D)** | 25.0% (3/12) | **100.0% (12/12)** | **+75.0%** |
| **vs Harvest Timing (V009-B)** | 33.3% (4/12) | **91.7% (11/12)** | **+58.4%** |
| **vs Diversified (V004-B)** | 41.7% (5/12) | **100.0% (12/12)** | **+58.3%** |
| **vs Dynamic Clusters (V008-D)**| 58.3% (7/12) | **100.0% (12/12)** | **+41.7%** |
| **vs Melon Flooder** | 100.0% (12/12) | **100.0% (12/12)** | 0.0% |
| **vs Balanced Optimizer** | 100.0% (12/12) | **100.0% (12/12)** | 0.0% |
| **vs Starter** | 100.0% (12/12) | **100.0% (12/12)** | 0.0% |
| **vs Random** | 100.0% (12/12) | **100.0% (12/12)** | 0.0% |
| **OVERALL MATRIX** | **70.0% (76/108)** | **99.1% (107/108)** | **+29.1%** |
