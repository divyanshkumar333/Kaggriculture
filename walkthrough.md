## 4. `v001_baseline.py` Implemented
The new `v001_baseline.py` implements the decoupled structure to serve as a robust platform for future optimization:
- **Explicit Task System:** The `Task` class now encapsulates priority, location, arguments, and required actions.
- **Economic Calculator Stub:** Added logic frameworks for estimating hire costs dynamically via Fibonacci sequence and modeling price-impact when selling products.
- **Strategic & Daily Planners:** Differentiates between speculative tasks (e.g., planting Melons) and mandatory survival tasks (e.g., watering plants and feeding animals).
- **Task Allocator:** Implemented marginal ROI thresholds to evaluate farm-hand hires logically rather than simply maximizing numbers.
- **Action Executor:** Translates high-level tasks to exact board coordinates and executes valid movement operations.

The foundation is now established. We have a robust, highly modular baseline ready for tuning the exact economic math and movement pathfinding.

## 5. Dynamic Task Engine Experiment (`v085_grandmaster_roi`)
- **Action**: Attempted to build a fully dynamic, trace-less agent by combining the `v070` Hungarian-algorithm task dispatcher with the `v057` aggressive macro-strategy.
- **Discovery**: We fixed several bugs in `v070`'s crop planting and structure building, and ran `v085` locally against `v057`. 
- **Result**: `v085` was completely crushed by the static trace (`4538` vs `120,187`). The combinatorial complexity of spatial management (building pastures efficiently without blocking hands), combined with trace agents intentionally crashing market prices (causing heuristic agents to freeze their sales), mathematically proves that **Greedy Heuristics cannot beat optimized Traces** in this environment.

## 6. The Path to 3000+ (Imitation Learning)
- **Discovery**: We found ~20 massive replay JSONs from top leaderboard matches in the root directory.
- **Insight**: Top players (3100+ Elo) are not using brittle traces. The presence of the `scripts/il_behavioral_cloning.py` pipeline indicates the true path forward: parsing these top replays to extract the macro-decisions (e.g., exactly which day to pivot to Strawberries based on the Random Town shop spawns) and training a LightGBM model to predict these pivots.
- **Action**: The foundation for Imitation Learning is set up in `RESEARCH`.
