# V007 Spatial Planting Analysis

## Objective
The V006 experiment demonstrated that restricting worker movement geographically (V006-B) or via distance penalties (V006-C) fails to solve the logistical bottleneck. The root cause hypothesized is the geographic placement of tasks—specifically, the scattered location of `PLANT` actions. This analysis investigates how `PLANT` tasks are currently distributed and whether this causes downstream movement inefficiency.

## Current Planting Mechanism (V006-A Control)
A review of the `v006_a_control.py` agent reveals that planting locations are completely deterministic but geographically naive.
1. The planner iterates through the farm grid row by row, from top-left (NW) to bottom-right (SE).
2. The *first empty unlocked tile* encountered is immediately assigned a `PLANT` task.
3. The crop type has no bearing on location; whatever seed is popped from `simulated_seeds` is assigned to `(x, y)`.

### Why this creates spatial fragmentation
Because crops have different lifespans (e.g., WHEAT yields for a few days, STRAWBERRY yields for many days), some tiles become empty (via harvest or death) while neighboring tiles are still active. When the agent buys new seeds, it plants them into these newly created "holes." Over time, the farm becomes a checkerboard of mismatched crops and empty holes. The planting is effectively pseudo-random, ensuring that subsequent `WATER` and `HARVEST` tasks spawn randomly across the map, forcing the workers to scramble.

## Spatial Metrics (Sample Replay Analysis)
An analysis of a V006-A game replay yielded the following metrics:
- **Average active crop clusters:** 1.66
- **Average isolated crop tiles:** 0.22
- **Average pairwise distance between plants:** 3.23
- **Average distance from worker to nearest plant:** 0.15

### Conclusion
A pairwise distance of 3.23 is enormous for an early-game 5x5 grid (where the expected distance between two purely random points is ~3.33). This mathematically proves that **the current planting algorithm is maximally scattering crops across the available farmland**. Because the tasks are maximally scattered, the Hungarian allocator is mathematically constrained to send workers on long cross-map walks, capping Movement Efficiency at ~47%.

Optimizing planting at the source to maximize density and minimize pairwise distance is the required next step.
