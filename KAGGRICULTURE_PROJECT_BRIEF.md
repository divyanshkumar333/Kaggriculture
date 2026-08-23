# Kaggriculture Project Brief

## Competition Goal
Maximize end-of-season bank balance in the Kaggriculture Kaggle competition.
Target skill rating: ~3135.8.
The objective is to optimize the entire economic system over a 30-day (720 turns) season.

## Rules & Mechanics
- **Grid:** 10x10 farm grid, divided into 4 quadrants (5x5 each). Start with NW unlocked.
- **Season Length:** 30 days, 24 turns per day = 720 turns total.
- **Victory Condition:** Most coins in the bank at the end of the season.
- **Actions:** 1 main farmer, plus N farm hands hired per day. Each can act (move, plant, water, harvest, feed, fertilize, build, drop, pickup).
- **Market Limit:** Max 10 market orders per turn. Order processing happens 1 unit at a time, concurrently with the opponent.
- **Shed:** Inventory limit of 100 non-seed items. Excess drops at end of day are discarded.
- **Watering/Feeding:** Must be done daily. 2 consecutive unwatered days -> weeds. 2 consecutive unfed days -> animals escape.
- **Weeds:** Small chance (0.5%) per empty unlocked tile at end-of-day.

## Observation Model
- `player`: 0 or 1
- `day`, `hour`: 0-29, 0-23
- `farms`: Public state of both players (money, tiles, farmer pos, hands pos, unlocked quadrants, hires today).
- `private`: Private state (shed, seeds, inventories).
- `market`: Shared market inventory and prices.
- `town`: Shared list of unlocked shops (which consume products).

## Action Space
- **Farmer/Hand Actions:** NORTH, SOUTH, EAST, WEST, PASS, PICKUP, DROP, PLANT, WATER, HARVEST, FERTILIZE, PLACE, FEED, COLLECT_FERTILIZER, CARE, BUILD_COOP, BUILD_PASTURE, DIG.
- **Market Actions:** BUY_SEED, BUY_ANIMAL, BUY_PRODUCT, SELL, HIRE, BUY_LAND.

## Economic Model
### Crops & Animals
- **Wheat:** One-time. Cost 10. Base 25. Yield window starts day 2, max day 4. Base yield 0.8/tile/day.
- **Carrot:** One-time. Cost 20. Base 35. Yield window starts day 2, max day 3. Base yield 0.75/tile/day.
- **Tomato:** Ongoing. Cost 50. Base 60. 4 yields total. Base yield 0.33/tile/day.
- **Strawberry:** Ongoing. Cost 100. Base 120. 4 yields total. Base yield 0.24/tile/day.
- **Melon:** One-time. Cost 80. Base 250. Yield window starts day 5, max day 10. Base yield 0.55/tile/day.
- **Goose/Egg:** Ongoing. Cost 300. Base 50. Needs Coop. Base yield 1.0/tile/day.
- **Cow/Milk:** Ongoing. Cost 400. Base 160. Needs Pasture. Base yield 0.5/tile/day.
- **Sheep/Wool:** Ongoing. Cost 500. Base 200. Needs Pasture. Base yield 0.33/tile/day.

### Costs
- **Land:** NE ($1k), SW ($2k), SE ($4k).
- **Farm Hands:** Cost increases by Fibonacci sequence daily per hire (1, 1, 2, 3, 5...).
- **Fertilizer:** Cost 100 on market, or collected free from animals (1 per day).

### Dynamic Market Pricing & Price Impact
- Prices are driven by market inventory vs I0 (10,000).
- Price curves differ by resource. Premium resources crash fast in gluts.
- Selling large batches is highly discouraged for premium resources because each unit sold drops the price.

## Approved Architecture
The agent will be built with a decoupled architecture, separating planning from execution. The flow is:
`Observation -> State Parser -> Strategic Planner -> Daily Planner -> Task Allocator -> Action Executor`

1. **State Parser:** Extracts the observation into queryable models.
2. **Economic Calculator:** Estimates expected revenue, input cost, expected profit, actions required, time to first revenue, production over remaining season, tile utilization, worker/action utilization, and fertilizer opportunity cost. Evaluates "Expected Profit per Action" and "Expected Profit per Tile-Day." Models market price impact.
3. **Strategic Planner:** Determines high-level goals based on configurable strategy modes and the Economic Calculator. Manages cash reserves and evaluates economically justified land expansion.
4. **Daily Planner:** Maps strategic goals to explicit daily tasks. Understands deadlines and prioritizes mandatory survival tasks (watering, feeding, harvesting before decay) over speculative economic tasks.
5. **Task Allocator:** Explicit Task System (priority, deadline, location, assigned worker). Assigns tasks to the main farmer and calculates marginal ROI to decide whether to HIRE farm hands.
6. **Action Executor:** Translates assigned tasks into exact actions/movements.

## Strategic Hypotheses
The following must be treated as configurable hypotheses to be validated through experiments:
- [HYPOTHESIS] Mixed farm is better than specialized farming.
- [HYPOTHESIS] Animals + fertilizer provide the best synergy.
- [HYPOTHESIS] Early land expansion is optimal (requires ROI validation).
- [HYPOTHESIS] Trickle-selling is always superior to bulk-selling.
- [HYPOTHESIS] Farm hands should be hired aggressively up to action limits.
- [HYPOTHESIS] Specific crops dominate others in particular market phases.

## Experiment & Benchmark Methodology
- **Experiments Script:** Supports multiple games, multiple random seeds, automatic side swapping, and comprehensive metrics (win rate, mean, median, min, max, std dev of final money, crash/error counts, market/production revenue). Exports results to `experiments/results.json`.
- **Strategy Modes:** Experiments evaluate explicit modes (e.g., `FARMER_ONLY`, `AGGRESSIVE_WORKERS`, `MARKET_FOCUSED`, `CROP_FOCUSED`, `ANIMAL_FERTILIZER`, `BALANCED`, `OPPORTUNISTIC`).
- **Regression Testing:** A new agent must reliably beat the previous best agent across the deterministic benchmark suite.
- **Reference Opponent:** `melon_maxxer` (baseline reference implementation).

## Tracking Best Agents
- **BEST_LOCAL_AGENT:** `v001_baseline.py`
- **BEST_LOCAL_SCORE:** ~$29,433 (vs starter, exact economics)
- **BEST_KAGGLE_AGENT:** N/A
- **BEST_KAGGLE_RATING:** N/A

## Milestones
- **[COMPLETED] Milestone 1:** Produce a reliable local agent that completes 720 turns without catastrophic failures.
- **[COMPLETED] Milestone 2:** Beat random consistently.
- **[COMPLETED] Milestone 3:** Beat starter consistently.
- **[COMPLETED] Milestone 4:** Beat Melon Maxxer consistently.
- **[COMPLETED] Milestone 5:** Implement Exact Economic Engine (Step 5).
- **[IN PROGRESS] Milestone 6:** Develop specialized strategy variants (V001-A, B, C) and find the strongest local strategy.
- **Milestone 6:** Find the strongest local strategy.
- **Milestone 7:** Submit to Kaggle.
- **Milestone 8:** Analyze real Kaggle episodes.
- **Milestone 9:** Iterate toward the ~3135.8 target.

## Current Assumptions and Known Uncertainties
- **Assumptions:** Official documentation accurately defines game mechanics.
- **Uncertainties:** Exact scaling of Town Shop demand interactions; actual marginal ROI cutoffs for farm hand hiring in mid-game states.

## Benchmark Results: Step 5 (Exact Economic Engine)

We updated `EconomicCalculator` in `v001_baseline.py` to perfectly replicate the environment's pricing model (`_shape` functions, `MARKET_PARAMS`, sequential sell simulation, floor absorption). The behavior logic (when to plant, what to plant) was strictly preserved to isolate the economic model's impact.

**V001 Exact Economics Benchmark Results (10 games each):**
*   **vs random:** 100% win, Mean `$29,101.30` (Previous `$29,132.10`)
*   **vs starter:** 100% win, Mean `$29,433.80` (Previous `$29,229.97`)
*   **vs melon_maxxer:** 100% win, Mean `$28,320.50` (Previous `$28,186.17`)

**Conclusion:** The exact economic modeling slightly improved the final bank balance in contested scenarios (+0.7% vs starter, +0.5% vs melon_maxxer) and performed neutrally vs random (-0.1%). The agent now correctly halts bulk-sell orders right as the marginal unit hits $1, preventing it from wasting time/inventory pushing down prices unnecessarily. The primary benefit of this phase is that future strategic variations (Step 6) will now be optimized against the true economic landscape.
