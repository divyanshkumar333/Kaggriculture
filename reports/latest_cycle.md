# Autonomous Research Loop: Cycle 1

## CURRENT VERIFIED CHAMPION
`V032` (Deployed as `main.py`). The true Kaggle submission is a frozen replay-execution artifact, not a dynamic agent, containing an embedded base64 trace spanning 720 steps. The `V051` logic exists locally but was never actively packaged.

## CURRENT VERIFIED COMPETITIVE BASELINE
`V025-A` (Aggressive Cows). This remains our strongest dynamic agent capable of localized reaction.

## BEST LOCAL H2H RESULT
`V025-A` dominates internal heuristic candidates (`V014`, `V085`, `V026`) but immediately fails against high-labor meta agents that pivot out of early cattle.

## CURRENT PUBLIC META
The September 2026 Kaggle meta (3000+ Elo) operates on a **Cow $\rightarrow$ Strawberry Transition**. 
- Opening: Rapid liquidation to afford 2-3 cows.
- Midgame: Flooding the market with milk to capture the $160 $\rightarrow$ $50 spread.
- Transition: Surging worker counts to **10–14 units** to plant up to 40 strawberries just as the milk market collapses to $1.

## LATEST KAGGLE EVIDENCE
Empirical replay analysis (`RESEARCH/meta/current_meta_20260919.json`) proves the median top-tier worker count is **11**, completely contradicting the prior repository claim of a strict 6-worker ceiling.

## TOP FAILURE MODE
**The Milk Glut Trap.** `V025-A` blindly continues to hoard cows and feed them even when the shared market milk inventory hits 100+ units. It sells milk at $1 while starving its own labor force, ultimately suffering a terminal cash collapse.

## TOP META GAP
**What actually separates our best agent from the current 3000+ meta?**
*Dynamic Labor Scaling & Sector Reallocation.* Our agents lack a state transition. They run one macro-policy for 720 turns. The meta agents possess a distinct **branch point**: when milk prices plummet, they explicitly stop buying cows and divert 100% of marginal capital to farmhands to tend high-margin strawberries. 

## LATEST EXPERIMENT
**CRN Paired-Seed Benchmark & Worker Cap Sweep**
- Swept worker caps from 6 through 14 against a mixed meta panel (V025-A, Strawberry-Flywheel, Random).
- Implemented `win_score` (W=1, T=0.5, L=0) fitness on identical seeds.

## W/T/L
*Aggregated Head-to-Head benchmark results from local engine (1.32.7)*
- V025-A (Baseline) vs Strawberry Flywheel: **0W - 0T - 16L**
- V032 (Trace Player) vs Strawberry Flywheel: **0W - 0T - 16L**

## WIN SCORE
Baseline `V025-A` Win Score against adversarial meta: **0.00**

## CONFIDENCE INTERVAL
High. Identical seed matching (CRN) isolates the decision divergence perfectly. The failure is structural, not stochastic.

## ADVERSARIAL RESULT
`v059_strawberry_flywheel.py` perfectly counters `V025-A`. The flywheel agent explicitly waits for V025 to crash the milk market, purchases seeds, and rides the unaffected strawberry margins to a $40k+ victory.

## DECISION
**REJECT** all current heuristic modifications to V025-A. 
The agent architecture requires an explicit **Policy Portfolio / Branching state**, rather than incremental changes to the existing Hungarian assignment loop.

## NEXT EXPERIMENT
**Build the Meta-Adaptive Market Spoiler (Dynamic Cow Expansion limit)**
We will build a portfolio agent with two explicit states:
1. `COW_RUSH` (Turns 0 - 200)
2. `STRAWBERRY_PIVOT` (Turns 201 - 720)
The branch will trigger explicitly when `market.prices["MILK"] < 50` OR `market.inventory["MILK"] > 60`. We will evaluate if this singular macro-branch point is sufficient to defeat the current Kaggle meta.
