# V001 Ceiling Analysis

To understand why V001 tops out at ~$29k, we analyzed the metrics from the exact economic baseline benchmark (vs random). 

## Diagnostic Metrics (Averages over 720 turns)
*   **Final Money:** $29,101
*   **Total Revenue:** $30,872
*   **Total Spending:** $4,724
*   **Seed Spending:** $3,741 (approx. 46 Melon seeds)
*   **Worker Spending:** $982
*   **Melon Plants Harvested:** 27
*   **Melon Units Sold:** 156
*   **ActionExecutor "Planted" metric:** 2,238
*   **Worker Useful Actions:** 2,223
*   **Worker Movement Actions:** 1,396
*   **Worker Idle Turns:** 551

## Major Bottlenecks (Ranked by Estimated Impact)

### 1. The Phantom Task Bug (Estimated Loss: $3k - $5k)
*   **The Issue:** `DailyPlanner` checks `if self.state.seeds.get("MELON", 0) > 0` and then creates a `PLANT` task for *every single empty tile* (up to 25). It does not decrement a local seed counter while planning.
*   **The Consequence:** If the agent has 1 seed and 20 empty tiles, it creates 20 `PLANT` tasks. 
    1.  `TaskAllocator` sees 20 unassigned tasks and aggressively hires farm hands, wasting money.
    2.  `ActionExecutor` dispatches multiple workers to plant. The first worker consumes the 1 seed. The remaining 19 workers execute `PLANT` with 0 seeds, wasting their turn (the environment silently ignores it).
    3.  Because `ActionExecutor` blindly assumes `PLANT` succeeds, it recorded an absurd 2,238 plants, while only 46 seeds were actually purchased and 27 plants actually reached maturity.
*   **Impact:** Massive waste of worker turns and unnecessary hiring costs. Fixing this will dramatically increase worker efficiency and reduce overhead.

### 2. Land Expansion Ignored (Estimated Loss: $15k+)
*   **The Issue:** The agent never buys the `NE`, `SW`, or `SE` quadrants.
*   **The Consequence:** The farm is hard-capped at 25 tiles.
*   **Impact:** Once the 25 tiles are fully utilized, the agent's revenue generation hits a hard ceiling. A single quadrant of Melons (say 15 active plants averaging 6 units each) produces ~90 melons per harvest cycle. At an average sell price of ~$190, that's $17k per cycle. With 3 cycles in a season, 1 quadrant yields $51k gross. Unlocking a second quadrant for $1k early on would essentially double the gross production limit.

### 3. Suboptimal Selling & Shed Management (Estimated Loss: $2k - $4k)
*   **The Issue:** The agent aggressively sells everything up to the $1 floor.
*   **The Consequence:** Melons have a high base price ($250) but a `sq` curve above `I0`. When 90 melons hit the market simultaneously, the price rapidly tanks. The agent sells them all the way down to $1, drastically reducing the average sale price. 
*   **Impact:** By not establishing a `min_sell_price` (e.g., stopping when Melon price drops to $100 and waiting for town consumption), the agent throws away premium value.

### 4. Zero Fertilizer / Animal Usage (Estimated Loss: Unknown, likely high)
*   **The Issue:** No animals are bought, so no fertilizer is generated.
*   **The Consequence:** Melons only receive the base watering bonus. With fertilizer, the bonus doubles.
*   **Impact:** For ongoing crops, fertilizer doubles output. For one-time crops like Melon, it significantly extends the yield. Ignoring this entirely leaves free yield on the table.

## Conclusion
The agent is currently playing a "Micro-Farm" strategy. It completely maxes out the starting 25 tiles (and wastes massive effort on phantom tasks trying to over-plant them), but fails to scale operations to the rest of the board. 

**Immediate Fix Required for V002-A (Control):** The Phantom Task Bug must be fixed in the `DailyPlanner` to establish a true, bug-free baseline before tweaking economic variables.

**Path to 3135.8:**
1. Fix phantom tasks.
2. Parameterize strategy to support `min_sell_price` (Smart Market).
3. Unlock land expansions dynamically.
4. Diversify crops to avoid crashing the Melon market.
