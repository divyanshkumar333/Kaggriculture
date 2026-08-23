# Spatial Scheduling Analysis

## Current Routing Behavior
In `v001_baseline.py` (and the expansion variant), worker assignment occurs in `ActionExecutor.execute`. For each worker (the main farmer, then each hired hand in order):

```python
field_tasks.sort(key=lambda t: (t.priority, abs(t.location[0] - ux) + abs(t.location[1] - uy)))
target = field_tasks[0]
```

### The Root Cause of Unnecessary Travel
The sort key is a tuple: `(priority, manhattan_distance)`. Python tuples sort lexicographically, meaning the first element `priority` completely dominates the sort.

Because task priorities are hardcoded (e.g., `WATER=0`, `HARVEST=10`, `PLANT=20`), a worker will **always** choose a `WATER` task across the entire map over a `HARVEST` task on the tile they are currently standing on. 

This causes two major issues on expanded farms:
1. **Stampeding**: When a day starts, all plants need watering. All workers target the closest unwatered plant to them. As the day progresses, workers end up criss-crossing the map to reach the remaining high-priority watering tasks, spending all their time moving.
2. **Ignored Local Work**: A worker standing next to an empty tile with seeds in their pocket will ignore planting (priority 20) to walk 15 tiles away to water a plant (priority 0), effectively wasting 15 turns for 1 action, when they could have performed the priority 20 action instantly.

## Planned Improvements (Step 6I)

### A. New Metrics
We will add tracking to `MetricsTracker` and `GameState` for:
- `worker_assigned_distances`: Average distance to assigned task.
- `watering_misses` / `crop_deaths`: Detected by comparing the previous state's plants to the current state (if a plant becomes a weed or vanishes prematurely).
- `movement_efficiency`: Ratio of useful actions to total actions.

### B. Worker Locality Policy (Task Score)
Instead of a strict tuple sort, we will convert the priority system into a continuous score:
`task_score = urgency + economic_value - travel_cost`
- A watering task with only 1 turn left before death has near-infinite urgency.
- A watering task early in the day has high economic value but finite urgency, so a worker might prefer to harvest a crop right next to them first.

### C. Regional Assignment
For expanded farms, workers will be assigned "home regions" (NW, NE, SW, SE) and strongly prefer tasks within those regions. A heavy penalty will be applied to cross-region tasks, unless the worker's home region is empty or another region faces an imminent crop death.

### D. Controlled Experiments
We will test 3 variants:
- **Variant A**: V001.1 Control (current tuple-based routing)
- **Variant B**: V001.1 + Locality Policy (no expansion)
- **Variant C**: V001.1 + Locality Policy + Expansion

This will isolate whether spatial locality improves the dense 5x5 farm, and whether it rescues the 10x10 farm from the travel-time trap.

## 5. Experiment Results and Conclusion

The 270-game benchmark (see `V001_SPATIAL_EXPERIMENT.md`) conclusively proved that the simple greedy locality fix (Variant B) **fails** to improve the agent. It paradoxically increased total movement distance and reduced efficiency. The rigid regional constraint (Variant C) failed catastrophically.

The root cause of Variant B's failure is the "stranding effect": workers greedily pick nearby low-value tasks and ignore urgent far-away tasks until they become critical, at which point the workers are forced to cross the entire map to save them, completely eliminating the benefit of the local choice.

### Next Steps (Step 6G/J)
Tuning these weights with Optuna will not resolve the structural issue of greedy task assignment. A fundamentally different multi-agent task allocation algorithm is required for `TaskAllocator` to solve the global routing problem (e.g. global assignment optimization using the Hungarian algorithm, or dynamic load balancing across flexible zones) before land expansion can become viable.
