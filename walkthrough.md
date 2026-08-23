## 4. `v001_baseline.py` Implemented
The new `v001_baseline.py` implements the decoupled structure to serve as a robust platform for future optimization:
- **Explicit Task System:** The `Task` class now encapsulates priority, location, arguments, and required actions.
- **Economic Calculator Stub:** Added logic frameworks for estimating hire costs dynamically via Fibonacci sequence and modeling price-impact when selling products.
- **Strategic & Daily Planners:** Differentiates between speculative tasks (e.g., planting Melons) and mandatory survival tasks (e.g., watering plants and feeding animals).
- **Task Allocator:** Implemented marginal ROI thresholds to evaluate farm-hand hires logically rather than simply maximizing numbers.
- **Action Executor:** Translates high-level tasks to exact board coordinates and executes valid movement operations.

The foundation is now established. We have a robust, highly modular baseline ready for tuning the exact economic math and movement pathfinding.
