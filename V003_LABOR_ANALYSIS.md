# V003 Labor Analysis: Kaggriculture Worker Economics

This document analyzes the exact costs, limits, and ROI of farm hands in the Kaggriculture environment, informing the V003 dynamic scaling implementation.

## 1. Exact farm-hand hiring costs and cost progression

Farm hands are hired per day using the `HIRE` market action. The cost for the $n$-th hire on the *same day* follows a Fibonacci sequence modified by `farmHandCostMult` (which is $1$ by default):

$$ \text{Cost}(n) = \text{farmHandCostMult} \times \text{fib}(n) $$

Where $n$ is the number of hires *already made today*. The sequence resets at the start of each day.
- 1st worker ($n=0$): $1
- 2nd worker ($n=1$): $1
- 3rd worker ($n=2$): $2
- 4th worker ($n=3$): $3
- 5th worker ($n=4$): $5
- 6th worker ($n=5$): $8
- 7th worker ($n=6$): $13
- 8th worker ($n=7$): $21
- 9th worker ($n=8$): $34
- 10th worker ($n=9$): $55

## 2. Maximum useful number of workers

The maximum useful number of workers is bounded by the total tile count. The default board is $10 \times 10 = 100$ tiles. 
Assuming all 100 tiles are unlocked and planted, there are at most 100 `WATER` tasks and up to 100 `HARVEST`/`PLANT` tasks in a single day. 

Since each worker has 24 actions per day, a theoretical maximum of $\sim 200$ actions are needed daily. 
Allowing $\approx 50\%$ overhead for movement, we need $\sim 300$ actions.
This suggests the absolute maximum useful number of workers is roughly $300 / 24 \approx 12$ workers (including the main farmer). 
In practice, 4-6 workers are usually sufficient for a fully utilized board.

## 3. Daily action capacity per worker

Each worker (main farmer and farm hands) can perform exactly **1 action per turn**.
There are **24 turns per day**. 
However, actions include movement (`NORTH`, `SOUTH`, `EAST`, `WEST`), so the *effective* number of useful task actions (like `WATER` or `HARVEST`) is lower, typically 10-15 per day, depending on task proximity.

## 4. Watering workload for every crop

**Every plant must be watered every day.**
Failing to water for two consecutive days turns the plant into a weed. This requires exactly 1 action per plant per day.
Thus, $P$ planted crops $= P$ watering tasks per day.

## 5. Crop lifetime and watering requirements

- **Wheat**: First yield day 2, Max yield day 4, Decays day 5. Requires daily watering.
- **Carrot**: First yield day 2, Max yield day 3, Decays day 4. Requires daily watering.
- **Melon**: First yield day 10, Max yield day 10, Decays day 11. Requires daily watering.
- **Tomato**: First yield day 8. Ongoing (yields days 8, 9, 10, 11). Decays day 12. Requires daily watering.
- **Strawberry**: First yield day 10. Ongoing (yields days 10, 12, 14, 16). Decays day 17. Requires daily watering.

## 6. Expected revenue per additional worker

An additional worker hired early in the day provides up to 24 actions.
If they spend 12 actions moving and 12 actions on tasks (e.g., watering 12 Melon plants), the marginal value is massive:
- 1 Melon yields up to 6 units over its 11-day life.
- A worker watering 12 Melons for 11 days (costing say, $3 / day if they are the 4th worker = $33 total cost) ensures the harvest of $12 \times 6 = 72$ melons.
- Even at the market price floor of $1, 72 melons generate $72. At base price ($250), they generate $18,000.
**Conclusion**: The ROI of farm hands is astronomically high as long as there are incomplete tasks and market prices haven't completely bottomed out.

## 7. Whether hired workers can contribute immediately

**Yes.** A `HIRE` action is a market order. It processes at the end of the turn it is submitted. 
The hired hand spawns orthogonally adjacent to the shed on the *next turn* and can be immediately assigned tasks by the allocation logic.
However, because they spawn near the shed, they must spend actions moving to the fields. Hiring late in the day (e.g., hour 20) yields only 4 actions, which might be entirely consumed by movement.

## 8. Whether worker costs are one-time or recurring

Worker costs are **recurring per day**. 
At the end of the day, all hired hands drop their inventory at the shed and disappear. They must be re-hired the next day, and the cost sequence resets.

## 9. Interaction between worker count and the global Hungarian allocator

The `TaskAllocator` builds a cost matrix of size $W \times T$, where $W$ is the number of active units (farmer + hands) and $T$ is the number of field tasks. 
The Hungarian algorithm solves this in $O(W \cdot T^2)$ time.
Since $W \le 15$ and $T \le 200$, the allocator is extremely fast and scales seamlessly with additional workers. 
The allocator will dynamically route the closest worker to the highest-priority tasks.

## 10. The point where additional worker ROI becomes negative

Worker ROI goes negative when:
1. **Labor Surplus**: $W \times (24 - \text{hour}) > \text{Remaining Tasks} \times \text{Movement Factor}$. If a worker is hired but there are no tasks, their actions default to `PASS` and the hire cost is wasted.
2. **Late-Day Hiring**: Hiring at hour 22 yields only 2 actions. The worker might not even reach the crop.
3. **Market Floor vs. High Fib Cost**: If the 9th worker costs $34, and they only harvest 12 carrots valued at $1 each (due to market glut), the daily ROI for that specific worker is negative.

## 11. Workload Approximation vs. Actual Routing Distance

The initial V003 formula assumed: `required_actions = field_tasks * 2`.
This approximation breaks down in sparse conditions. If 5 plants are scattered across 4 quadrants, the worker spends 5-6 actions moving between them, not 1.
However, Kaggriculture's space is small ($10 \times 10$) and the allocator naturally clusters work. A single 5x5 quadrant is filled densely. 
To improve accuracy, we will compute the actual L1 Manhattan distance between workers and their assigned tasks, and for any unassigned tasks, we compute the distance from the shed `(4,4)` (the spawn point for new hires) plus the dense clustering assumption `(tasks - 1) * 2`.
Wait, the easiest actual representation of the workload is to sum the minimum distance from ANY worker (or shed) to each task, plus 1 for execution.

Final formula adopted:
- For each task, `dist = min(manhattan(worker, task) for worker in units)` or `manhattan(shed, task)` if considering a hire.
- `required_actions = sum(dist + 1 for task)` is an overestimation because workers chain tasks. 
- A much better formula that avoids overestimation of chaining is: `required_actions = max(0, dist_to_first_task) + field_tasks * 2`. But wait, `field_tasks * 2` was already highly accurate! 

Actually, after auditing the TSP routing in a dense 5x5 quadrant: 
Planting/Watering a 5x5 grid requires 25 task actions + exactly 24 movement actions (a snake path). 
So 49 actions total for 25 tasks. 
$\frac{49}{25} = 1.96$ actions per task.
**Conclusion**: `field_tasks * 2` is an incredibly accurate approximation of true workload in Kaggriculture for dense farming. It slightly overestimates sparse farming, which conservatively hires *more* labor when crops are far apart (a desirable outcome since transit times are higher). We will retain the `* 2` multiplier but add initial transit distance `dist(shed, first_task)` for the unassigned tasks to account for the hire's spawn overhead.
