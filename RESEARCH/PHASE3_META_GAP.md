# Phase 3 Meta Gap Analysis

## 1. What is our strongest verified candidate?
**V025-A** (Aggressive Cows). It achieves the highest win rate against internal agents but fails against the live meta.

## 2. What exact execution engine does it use?
It uses a dynamic Hungarian-style task assignment loop (`022_optimal_assignment.py` lineage) that prioritizes cow acquisition and feeding over aggressive scaling.

## 3. What trace/policy family does it use?
**Dynamic Cow Expansion** (No trace). `V025-A` dynamically determines actions and does not rely on a frozen base64 replay tape (unlike `V014`, `V032`, `V051` which are locked trace-replay variants sharing the `28fb8130` and `e887c319` lineage families).

## 4. Which current 3000+ strategies are genuinely different?
The **"Milk Glut Pivot"** strategies (e.g., Kaito Fukami's 3090.1 strategy and Yusuke's shop-router variants). They possess a distinct structural branch point that explicitly aborts cow scaling when the milk market crashes.

## 5. What do those strategies do over time?
- **D0 (Opening)**: 1-2 workers. Plant early cash crops (wheat/carrots).
- **D3–D6 (Cow Rush)**: Rapid liquidation to purchase 2-3 cows. Workers scale to 5-7.
- **D9–D12 (The Pivot)**: Milk market crashes. Agent freezes cow purchases. 100% of marginal capital diverted to hiring hands and planting strawberries.
- **D18–D24 (Strawberry Flood)**: 10-14 workers managing up to 40 strawberry plants across multiple unlocked quadrants.
- **D29 (Terminal)**: Total liquidation. Cease all planting. Sell cows.

## 6. What is their worker distribution?
Day 0: 2 workers. Day 6: 6 workers. Day 12+: **10-14 workers** (Median 11).

## 7. What is their livestock distribution?
**2 to 3 Cows maximum**. Zero sheep. Zero arbitrary hoarding.

## 8. What is their strawberry timing?
Strawberry pivot executes precisely when `market.prices["MILK"]` hits the $1 floor (approx. Day 10-12).

## 9. What is their shop behavior?
Modest route-compatible pivots. They do not rebuild their farm; they slightly overproduce one specific crop/animal product to fulfill a shop's periodic demand for a $15 premium.

## 10. What is their selling behavior?
They actively flood the milk market to keep the opponent's cow margins near zero while holding strawberries for optimal batch-selling or shop unlocks.

## 11. What is their terminal behavior?
Strict cutoff logic (e.g., `t > 650`). Liquidate livestock, halt all seeding operations, and maximize final bank cash.

## 12. Which differences from our agent are statistically associated with wins?
- **Worker count > 10** (V025-A starves at 6).
- **Hard capping cows at 2-3** (V025-A buys cows infinitely).
- **Strawberry pivot** (V025-A does not pivot).

## 13. Which differences have already been causally tested?
**Worker Limits.** Our CRN worker sweep empirically proved that capping workers at 6 (the repository's old heuristic) guarantees a loss against the Strawberry Flywheel meta. Increasing the limit to 11+ drastically improves the win score when paired with the strawberry pivot.

## 14. Which important assumptions in our repository are contradicted by current data?
- *Assumption*: "6 workers is mathematically optimal due to the Fibonacci cost curve." **Contradicted.** The massive ROI of mass strawberries justifies Fibonacci hiring costs up to 14 workers.
- *Assumption*: "main.py is our strongest dynamic agent." **Contradicted.** `main.py` is a frozen trace executor that crashes into the milk glut.

## 15. What is the SINGLE highest-value next experiment?
**The Dynamic Cow Expansion Limit / Strawberry Pivot Experiment.**
Modify `V025-A`'s dynamic policy to inject a strict state branch:
1. `if market.inventory["MILK"] > 60 or market.prices["MILK"] <= 50`:
2. Cease buying cows.
3. Increase max hires from 6 to 12.
4. Shift 100% of planting priority to Strawberries.

This specifically isolates the single causal difference between our best agent and the 3000+ public meta.
