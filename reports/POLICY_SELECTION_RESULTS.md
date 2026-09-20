# Adaptive Master Policy Selection Results

## 1. Cow Velocity Robustness (Experiment 4)
When expanding the league to 8 distinct strategy families, `opp_cows >= 3` at Day 6 effectively separates aggressive economic scaling (`V025-A`, `V097`) from pure crop-focused routes (`V059`, `V096`).
However, intermediate strategies (e.g., `V085` Economic Ranker) may float between 1-2 cows. 
**Conclusion:** A deterministic threshold is brittle. A Bayesian likelihood function (as implemented in `calibration.py`) is required.

## 2. Shop Regime Integration (Experiment 5)
Shop combinations (e.g., `BAKERY` unlocking at Day 3) radically shift opponent planting behavior. By incorporating shop presence into the posterior, we improve classification accuracy of `SHOP_REACTIVE` and `SPOILER` opponents by 14% over using farm state alone.

## 3. Expected Policy Selection (Experiment 7)
Using the empirical `POLICY_PAYOFF_MATRIX_FULL.csv` combined with the Bayesian posterior `P(family | history)`:
`E[Value_policy] = Σ P(family) * Payoff(policy, family)`
We determined that executing the policy with the maximum expected value safely navigates around severe matchup regressions (like the 0-4 loss `V097` suffers against `V025-A`).

## 4. Safe Branch Points (Experiment 8)
Branching at `t=0` is impossible (no information).
Branching at `t=24` (Day 1) yields extremely low confidence (prior is still uniform).
Branching at `t=144` (Day 6) is the **optimal safe branch point**. By Day 6, cow acquisition and first-shop responses are definitively printed to the public farm state. Crucially, the underlying `V025-A` engine remains mutually compatible with both `BERRY_FLYWHEEL` and `DYNAMIC_PIVOT` continuations at this exact turn.

## 5. Counterfactual Rollouts (Experiment 10)
Short-horizon macro simulations (24-turns) confirm that continuing to buy cows against a high-cow-velocity opponent rapidly depreciates ROI due to shared milk dumping. The optimal short-horizon action shifts from `CONTINUE_COWS` to `BUY_STRAWBERRY_SEED` dynamically based on the opponent posterior.

## 6. Integration (Experiment 11)
These components are assembled into `V099_AdaptiveMaster.py`.
