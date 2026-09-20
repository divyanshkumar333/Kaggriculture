# Engine Compatibility and Mechanics Baseline

## 1. Environment Versions
- **LOCAL_ENGINE_VERSION**: `kaggle-environments == 1.32.7`
- **KAGGLE_NOTEBOOK_ENGINE_VERSION**: Inherits `1.32.7` (Kaggle docker image typically lags slightly behind latest PyPI or mirrors it precisely during active competitions).
- **KAGGLE_EVALUATOR_VERSION**: `1.32.7`. (Matchmaking uses the same strict versioning).

## 2. Runtime-Sensitive Behavior Matrix
For all future research, the official local engine behaves exactly as follows:

| Feature | Verified Behavior |
| :--- | :--- |
| **`step`** | Validated via `test_step_consistency.py`. Starts at `0` for both Seat 0 and Seat 1, ending at `719`. |
| **`day` / `hour`** | Calculated as `step // 24` and `step % 24`. Exactly 30 days of 24 hours. |
| **RNG & Seed Symmetry** | Matches share common random numbers (CRN) for town shop unlocks and weed spawns. |
| **Shop Unlocks** | Stochastic. A town shop unlocks every 3 days. Unlocks are drawn uniformly *with replacement*, meaning multiple instances of the same shop can stack demand. |
| **Weed Spawning** | Occurs at the end of every day (`step % 24 == 23`). 0.5% base chance on every unlocked, empty tile. |
| **Market Processing Order** | Orders are processed in the order they are appended to the `market` action array. Player 0 orders and Player 1 orders are interleaved by the engine. |
| **Order Limit** | Strictly capped at `maxMarketOrdersPerTurn` (10 orders per turn per player). Extras are dropped silently. |
| **Episode Termination** | Hard limit at step `720`. The winner is determined solely by maximum final bank cash (`farms[player]["money"]`). |

## 3. Simulator Throughput Implications
Given the high I/O overhead of standard engine logging in `1.32.7`, running 128-seed paired evaluation directly through `kaggle_environments.make("kaggriculture", debug=True)` is prohibitively slow for autonomous research loops. We must run matches with `debug=False` and capture raw JSON results directly for fitness evaluation.
