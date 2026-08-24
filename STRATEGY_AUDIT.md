# V001 Strategy Audit

## Strategic Decisions Currently Hard-Coded

| Decision | Current Logic | Parameterized? | Likely Impact | Experiment |
| :--- | :--- | :--- | :--- | :--- |
| **Crop Selection** | Exclusively plants `MELON` (`if self.state.seeds.get("MELON", 0) > 0: ... {"crop": "MELON"}`). | No | Prevents utilizing faster-growing crops or responding to town demands. | Compare Melon-only vs Mixed-farming. |
| **Planting Threshold** | Creates a `PLANT` task for every empty unlocked tile as long as seed inventory > 0, ignoring the actual *number* of seeds available. | No | Creates "phantom tasks" that trick the allocator into over-hiring and cause workers to execute invalid `PLANT` actions when seeds are exhausted. | Fix task generation to respect seed count; test planting limits. |
| **Seed Purchasing** | Buys up to 5 `MELON` seeds anytime seed count is 0 and money > reserve. | No | Stalls planting if seeds run out; batch size of 5 might be sub-optimal. | Parameterize seed buffer threshold and batch size. |
| **Harvest Policy** | Harvests instantly when `yield_units > 0` and `is_ready_to_harvest` is true. | No | Generally optimal to harvest ASAP, but coordinating harvests with market spikes might be better for ongoing crops. | Coordinate harvest timing with market prices. |
| **Worker Hiring** | Hires a worker if `unassigned_field_tasks > active_workers` and `ROI (hardcoded 15) > hire_cost`. | No | High impact. Phantom tasks cause over-hiring. Hardcoded ROI ignores actual late-game or actual crop value. | Dynamic ROI calculation based on season remaining and crop value. |
| **Worker Allocation** | Greedy assignment to the nearest task based on Manhattan distance. | No | Can cause workers to cross paths or chase moving tasks inefficiently. | Better spatial partitioning or task claiming. |
| **Land Expansion** | Completely ignored (no logic to buy `NE`, `SW`, `SE`). | No | Massive impact. Limits maximum production ceiling to 25 tiles. | Implement ROI-based land expansion. |
| **Animal Purchasing** | Completely ignored (no logic to build coops/pastures or buy animals). | No | Misses out on steady income and free fertilizer. | Implement an animal-focused variant. |
| **Fertilizer Usage** | Completely ignored. | No | Halves the potential yield of ongoing crops and misses the +1 bonus on one-time crops. | Implement fertilizer distribution strategy. |
| **Cash Reserve** | Hardcoded to `50` coins. | No | Might be too small if a large hiring wave or seed purchase is needed. | Parameterize `cash_reserve`. |
| **Market Selling** | Sells any shed inventory where marginal price > $1, up to 10 units per turn. | No | "Dump everything above floor" strategy might prematurely crash prices instead of waiting for town consumption to push prices back up. | Parameterize `min_sell_price` and `batch_size`. |
| **Shed Management** | No explicit management; just relies on the market seller to empty it. | No | Risks dropping items at end-of-day if market floor is hit and shed fills up. | Safety valve to dump cheap items if shed reaches 90 capacity. |
| **Production Limits** | None. Will plant 25 melons if possible. | No | Saturated markets will drop Melon price to 1. | Cap concurrent plants of a specific crop based on market `T` value. |
