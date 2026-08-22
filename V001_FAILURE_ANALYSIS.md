# V001 Baseline - Failure Analysis

Based on the 30-game benchmark suite metrics, `v001_baseline.py` is capable of dominating `random`, `starter`, and `melon_maxxer`, achieving an average score of **$22,366**. However, the telemetry reveals massive economic inefficiencies and bottlenecks that, if fixed, could easily double or triple the agent's score.

## 1. The Shed Bottleneck & Price Threshold Collapse
**Observation**: 
From the generated metric `game_42_p0.json`, the agent achieved the following crop stats:
- **Melons Planted**: 246
- **Melons Harvested**: 3,489
- **Melons Sold**: 93
- **Melon Revenue**: $22,298

**Analysis**: 
The agent harvested 3,489 melons but only sold 93 of them. Where did the other 3,396 melons go? 
1. The agent has a hardcoded rule to only sell if `price > 50` (see `DailyPlanner.plan_tasks`).
2. Because melon price uses a logarithmic drop function, selling 93 melons increased the market inventory enough to drop the price to $50 or below.
3. The agent stopped selling melons, so they began accumulating in the shed.
4. The shed has a hard capacity of **100 items**. Once full, all newly harvested melons were permanently discarded.

**Conclusion**: The agent spent enormous amounts of labor and money ($2,000 in seeds, $990 in worker wages) harvesting melons that were immediately thrown into the void.

## 2. Monoculture Vulnerability
**Observation**:
The agent only plants Melons.

**Analysis**:
Because the agent only plants one crop, it is fully exposed to market saturation. When the melon price crashes, the agent has no alternative revenue streams. It does not plant Wheat, Carrots, or Strawberries, nor does it raise animals (which produce passive income and fertilizer). 
If it had diversified into animals or other crops when melon prices dropped, the workers (who were 99.4% utilized) could have generated productive value instead of harvesting discarded melons.

## 3. Naive Selling Rate
**Observation**:
The agent currently sells a maximum of 2 units of product per turn: `sell_qty = min(qty, 2)`.

**Analysis**:
The market accepts up to 10 orders per turn. By limiting itself to 2 items per task, and queuing only 1 task per product type, the agent is selling way too slowly, exacerbating the shed bottleneck. 

## 4. Land Expansion Ignored
**Observation**:
The agent never buys the NE, SW, or SE quadrants.

**Analysis**:
Despite hoarding $22k in the bank, the agent only farms the starting NW quadrant (25 tiles). Expanding the farm would allow more simultaneous crops and animals, scaling the economy linearly.

## Next Steps (Milestone 2 - Phase 5)
To push past 3000 rating, the next iterations (V001-A, B, C) must implement:
1. **Accurate Economic Model**: Replace the hardcoded `price > 50` heuristic with actual expected marginal profit calculations (fetching the exact market curve formulas from the environment code).
2. **Crop Diversification**: Implement a dynamic crop chooser based on the highest ROI crop currently available.
3. **Animal & Fertilizer Engine**: Integrate Cows/Sheep/Geese into the economy to utilize excess wheat and generate high-margin products + fertilizer.
4. **BFS Pathing**: Ensure the workers can navigate a dense farm filled with coops and pastures without getting stuck.
