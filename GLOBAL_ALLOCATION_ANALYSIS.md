# Global Task Allocation Analysis

## 1. The Architecture Flaw
The previous architecture (`v001_baseline` and variants) used a sequential greedy assignment:
```python
for ui, (ux, uy) in enumerate(units):
    field_tasks.sort(key=score_task)
    target = field_tasks.pop(0)
```
This is computationally cheap but structurally flawed because Worker 1's greedy choice can force Worker 2 into a terrible choice. If Worker 1 picks a nearby low-value task, they might leave an urgent distant task for Worker 2 (who is also distant). This "stranding effect" causes the average assignment distance to increase and crops to die.

## 2. Global Assignment Formulation
Instead of sequential choices, we construct a bipartite matching problem:
Let $N$ be the number of workers.
Let $M$ be the number of field tasks.
We construct an $N \times M$ cost matrix $C$ where $C_{i,j}$ represents the cost of assigning Worker $i$ to Task $j$.

The goal is to find an assignment that minimizes the total cost. This is the classic linear sum assignment problem, which can be solved optimally and deterministically using the Hungarian Algorithm (`scipy.optimize.linear_sum_assignment`).

## 3. Cost Function Design
The cost function $C_{i,j}$ must balance hard constraints (crop survival) with soft optimization (efficiency).

For Worker $i$ at $(ux, uy)$ and Task $j$ at $(tx, ty)$:
1. **Travel Distance**: $D = |ux - tx| + |uy - ty|$
2. **Task Urgency / Deadline**: 
   - A crop needs watering before the end of the second consecutive unwatered day. If $D > \text{deadline}$, the crop will die before the worker arrives. Cost = $\infty$.
   - If the task is urgent (e.g. `urgency_weight` in the baseline), we must guarantee it is assigned if physically possible. Cost = $-1000000 + D$ (massively incentivizes assignment, breaks ties by proximity).
3. **Economic Utility**:
   - For non-urgent tasks (e.g. planting, harvesting), we want to maximize economic value and minimize travel distance.
   - Cost = $D - \text{economic\_value}$

## 4. Task Bundling & Replanning
Since Kaggriculture is highly dynamic (weeds spawn, crops mature), we recalculate the global assignment *every turn*. 
To prevent workers from ping-ponging across the map, distance $D$ naturally acts as a soft stickiness factor (workers prefer tasks near their current location). We do not use hard regional boundaries (which failed in Variant C) because `linear_sum_assignment` will naturally handle load-balancing: if one quadrant has 10 tasks and 1 worker, the algorithm will mathematically justify sending a second worker from another quadrant if the utility outweighs the travel cost.

## 5. Implementation Strategy
We will replace the `field_tasks.sort` loop in `ActionExecutor` with `linear_sum_assignment`. 

**Variant D (`v001_global.py`)**: Uses global allocation without land expansion.
## 5. Experiment Results & Conclusion
The 270-game benchmark (`V001_GLOBAL_EXPERIMENT.md`) proved the Hungarian allocation architecture is a massive structural success:
- **Crop Deaths were completely eliminated (dropped from 9.8 to 0.0)** because the hard constraints flawlessly forced workers to prioritize dying crops, regardless of distance.
- **Routing efficiency skyrocketed**. Even on a fully expanded 10x10 farm (Variant E), the average assignment distance dropped to 1.28, and workers performed 936 useful actions (up from 394).

### The New Bottleneck: Market Saturation
While the spatial scheduling problem is officially solved, the agent's Final Bank dropped. The agent successfully expanded and doubled its physical production (harvesting 64 Melons instead of 37), but the Kaggriculture dynamic market penalized this oversupply. The sale price of Melons crashed to the $1 floor, capping total revenue at ~$33k despite massive increases in seed and land spending.

**Next Optimization:** The agent must adopt a multi-crop or market-aware strategy (e.g., crop diversification, holding inventory, or animal husbandry) to translate its newly optimized physical capacity into economic profit.
