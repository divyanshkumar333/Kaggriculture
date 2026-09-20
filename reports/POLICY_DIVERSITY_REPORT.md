# Policy Diversity & Non-Dominated Meta Report

## 1. The Full League Composition
We expanded the benchmark league from 3 to 8 distinct strategy families to evaluate generalization of the Opponent Model:
- **`V025-A` (Aggressive Cows)**: The baseline Cow Rush strategy. Infinite scaling of cows.
- **`V059` (Strawberry Flywheel)**: The adversarial anti-cow strategy. 0 cows, pure strawberry macro.
- **`V097` (Dynamic Pivot)**: A naive hybrid. Cows early, pivots to strawberries blindly when milk crashes.
- **`V085` (Grandmaster ROI)**: An economic ranker. Balances 2-3 cows with high-value crops.
- **`V057` (Generalized Spoiler)**: Frontruns market dumps to crash competitor margins.
- **`V070` (Dynamic ROI)**: Continuously shifts crop priority based on local ROI.
- **`V081` (Kaggle 83k Trace)**: A static replay capturing the broad public meta (hybrid cow/crop).
- **`V096` (12 Melon Opening)**: A specialized extreme crop rush leveraging Melon capital.

## 2. Non-Dominated Policies
Based on the full 8x8 empirical payoff matrix, we observe that the global meta remains strictly non-transitive.
There is **no globally dominant strategy**.
- **`V025-A`** dominates early-game crop rushes by starving them of capital via fertilizer dominance.
- **`V059`** dominates `V025-A` by ignoring the milk market entirely and riding the massive late-game berry ROI.
- **`V085`** is the most *robust* against unknown noise, maintaining a high floor but occasionally losing to the extreme spikes of `V059` or `V096`.
- **`V057` (Spoiler)** specifically counters `V097` by artificially causing a milk crash without actually buying cows, tricking `V097` into a fatal, unfunded pivot.

## 3. The Necessity of the Adaptive Master
Because no single policy is non-dominated across all matchups, the `V099_AdaptiveMaster` architecture is strictly required. By observing the opponent's public state (specifically cow velocity and shop regime) at Day 6, the Adaptive Master collapses the opponent's identity into a posterior distribution and selects the mathematically optimal counter-policy, breaking the local and global non-transitive loops.
