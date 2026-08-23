# V001 Baseline - Failure Analysis

**[UPDATE - 2026-08-23]:** The previous run of the baseline has been labeled as **PRE-FIX / INVALID BASELINE**.
The initial analysis identified severe economic bottlenecks where thousands of melons were discarded. However, further investigation discovered that this was actually caused by two critical implementation bugs, not just suboptimal strategy:
1. **Crash during sell phase:** The `DailyPlanner` was missing the `econ` dependency on initialization, causing the agent to silently crash the exact moment the first melon hit the shed. Kaggriculture falls back to a `PASS` action when an agent crashes, leaving the melons to rot.
2. **Infinite Harvest Loop:** Kaggriculture initializes `yield_units=1` immediately upon planting. The agent saw this and spammed `HARVEST` on unripe plants continuously, freezing the workers for 12 days straight.

After fixing these bugs, the baseline's score increased dramatically from `$1,757` to roughly `$29,000+`.

## Historical Pre-Fix Analysis (For Reference)

Based on the initial (flawed) 30-game benchmark suite metrics, `v001_baseline.py` achieved an average score of **$22,366**. However, telemetry revealed massive economic inefficiencies.

### 1. The Shed Bottleneck & Price Threshold Collapse
**Observation**: 
From the generated metric `game_42_p0.json`, the agent achieved the following crop stats:
- **Melons Planted**: 246
- **Melons Harvested**: 3,489
- **Melons Sold**: 93
- **Melon Revenue**: $22,298

**Analysis**: 
The agent harvested 3,489 melons but only sold 93 of them due to the dependency crash. The agent spent enormous amounts of labor and money harvesting melons that were discarded once the 100-item shed capacity was reached.

### 2. Monoculture Vulnerability
**Observation**:
The agent only plants Melons.

**Analysis**:
Because the agent only plants one crop, it is fully exposed to market saturation. When the melon price crashes, the agent has no alternative revenue streams.

### 3. Naive Selling Rate
**Observation**:
The agent currently sells a maximum of 2 units of product per turn: `sell_qty = min(qty, 2)`.

**Analysis**:
The market accepts up to 10 orders per turn. By limiting itself to 2 items per task, and queuing only 1 task per product type, the agent is selling way too slowly. (This has since been increased to 10).

### 4. Land Expansion Ignored
**Observation**:
The agent never buys the NE, SW, or SE quadrants.

**Analysis**:
Despite hoarding cash in the bank, the agent only farms the starting NW quadrant (25 tiles). Expanding the farm would allow more simultaneous crops and animals, scaling the economy linearly.

## Next Steps (Step 5 Optimization)
To push past 3000 rating, the next iterations (V001-A, B, C) must implement:
1. **Accurate Economic Model**: (In Progress) Replace heuristics with exact expected marginal profit calculations using the environment's pricing formulas.
2. **Crop Diversification**: Implement a dynamic crop chooser based on the highest ROI crop currently available.
3. **Animal & Fertilizer Engine**: Integrate Cows/Sheep/Geese into the economy to utilize excess wheat and generate high-margin products + fertilizer.
4. **BFS Pathing**: (Deferred) The grid is fully passable, so Manhattan routing is currently sufficient.
