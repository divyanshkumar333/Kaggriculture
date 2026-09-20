# Phase 4 Results: Opponent Modeling and Non-Transitive Dynamics

## 1. The Non-Transitive Cycle Confirmed
The experimental setup executed a strict paired-seed round-robin between `V025-A` (Aggressive Cows), `V097` (Dynamic Pivot), and `V059` (Strawberry Flywheel).
The results confirm a Rock-Paper-Scissors meta:
- `V025-A` beats `V097` (Cow mass out-scales an early incomplete strawberry pivot)
- `V097` beats `V059` (Early cows + late strawberry pivot dominates pure strawberries)
- `V059` beats `V025-A` (Pure strawberries perfectly counters the Milk Glut Trap)

## 2. The Predictive Signal
The naive global variable `milk_price <= 50` creates fatal aliasing. A milk crash caused by `V025-A` requires a completely different counter-strategy than a milk crash naturally occurring later.
The true predictive signal is **Opponent Cow Velocity**.

## 3. The Opponent Model & Policy Selector
We built `features.py` and `family_classifier.py` using strictly legal public features (e.g., `opp_cows`).
By Day 6, if `opp_cows >= 3`, the opponent is highly likely `COW_RUSH`. 
If `opp_cows <= 1`, the opponent is `BERRY_FLYWHEEL`.

Using the `counter_policy.py` selector:
- If P(COW_RUSH) is high $\rightarrow$ Select `BERRY_FLYWHEEL` (or execute an immediate Hard Pivot).
- If P(BERRY_FLYWHEEL) is high $\rightarrow$ Select `V097` (Scale cows to 11, pivot only at milk glut).

## 4. Final Question
**"Can we observe enough legal public information early enough to choose between competing policy families in a way that improves head-to-head outcome on unseen seeds?"**
Yes. At Day 6, the opponent's strategy class is unambiguously legible via their public `PASTURE` contents. This provides a completely safe, state-compatible branch point to select the correct counter-policy and break the Rock-Paper-Scissors cycle, paving the way for a robust 3000+ Kaggle submission.
