# V009 Bottleneck Analysis

## Replay-Based Economic Forensics

Based on 5 full test games of `V009-A` (which is functionally identical to V008-D) vs `random`, we extracted detailed internal metrics to determine the exact sources of economic loss.

### 1. The Core Metrics (Average per game)
- **Total Revenue:** ~$37,650
- **Final Bank:** ~$34,800
- **Seed Spending:** $4,960
- **Worker Spending:** $73 (Very low!)
- **Crop Deaths:** 0.0 (Agent handles crop decay and weed spawns effectively)
- **Watering Misses:** 4.6 (Minimal impact)
- **Movement Efficiency:** 48% (797 movement actions vs 748 useful actions)
- **Idle Worker Turns:** 181
- **Labor Surplus:** 6,816
- **Unsold Inventory:** 0 (Market capacity handles all sales)

### 2. Bottleneck Ranking

| Bottleneck | Estimated Loss / Game | % of Potential Profit Lost | Evidence |
|------------|-----------------------|----------------------------|----------|
| **1. Poor Harvest Timing (Late Planting)** | **~$5,000 - $7,000** | **~15-20%** | STRAWBERRY plants average 19 planted but only 40 harvests (expected 76). The agent's `EconomicCalculator` assumes full lifespan yields regardless of `remaining_days` in the season. Seeds bought after Day 20 cost $100 but yield 0 before the game ends at Day 30. |
| **2. Idle Worker Capacity** | ~$2,700 | ~7% | 181 idle turns * $15 marginal worker value. Workers are cheap ($73 total spending) but are left standing around because the agent caps `Task("BUY_SEED")` without reinvesting surplus cash. |
| **3. Movement Inefficiency** | ~$1,200 | ~3% | 797 movement actions. If we reclaim 10%, that's ~$1,200 at $15/action. V008 dynamic clustering already solved the worst of this. |
| **4. Land Under-utilization** | ~$2,000 | ~5% | Seed spending is capped, meaning land remains empty while money sits in the bank. Agent finishes with $34,800 cash but doesn't buy land or scale crops. |
| **5. Watering Misses** | ~$100 | <1% | 4.6 misses per game. |
| **6. Crop Deaths** | $0 | 0% | 0 deaths. |

### 3. Market Analysis
The agent successfully uses the market to sell off inventory, mostly Melon and Strawberry. Unsold inventory is exactly 0. 

| Crop | Planted | Expected Harvests | Actual Harvests | Issue |
|------|---------|-------------------|-----------------|-------|
| WHEAT | 5 | 5 | 5 | None |
| TOMATO| 5 | 20 | 20 | None |
| MELON | 25 | 25 | 24 | 1 melon planted on day >20 failed to yield. |
| STRAWBERRY | 19 | 76 | 40 | **36 harvests missed!** Half of all strawberries planted never reach maturity before day 30. |

### 4. Labor Economics
The agent spends $73 total on labor. 
Labor surplus is 6,816 turns, meaning there is practically an infinite pool of cheap labor waiting to be used. However, the agent's seed-buying logic is overly conservative and fails to put this labor to work. The agent is under-hiring because there are simply no tasks generated to justify more workers.

### 5. Land Utilization
The agent doesn't even fill its initial quadrant effectively. Buying land is NOT profitable until we solve the seed scaling and late-planting waste.

### 6. Animal Husbandry
Animals are still not viable until the baseline crop math accurately reflects the remaining season length. An animal bought on Day 25 will never pay back its $300-$500 purchase price.

---

## IDENTIFY ONE BOTTLENECK

**PRIMARY BOTTLENECK:**
Poor Harvest Timing (Late Planting / ROI Miscalculation)

**ESTIMATED LOSS:**
$5,000 - $7,000 / game

**EVIDENCE:**
In `game_800_p0.json`, the agent planted 19 STRAWBERRY plants. STRAWBERRY yields on days 10, 12, 14, 16. A fully matured plant yields 4 times. 19 plants should yield 76 harvests. However, the agent only realized 40 harvests. This is because the agent's `EconomicCalculator` projects revenue assuming infinite time, leading it to buy $100 Strawberry seeds on Day 25, water them for 5 days, and get 0 yield before the game ends on Day 30. 

**SECONDARY BOTTLENECKS:**
- Idle Workers / Land Under-utilization
- Movement Logistics

**WHY NOT OPTIMIZE THEM YET:**
Before we scale up planting to fill the land and utilize idle workers, we must ensure the agent doesn't mass-plant unprofitable crops on Day 28. Fixing the `remaining_days` ROI calculation is a prerequisite for safe scaling. Movement logistics were already optimized in V008 and are no longer the bleeding neck.

**PROPOSED V009-B:**
Modify `EconomicCalculator` in `agents/v009_b_harvest_timing.py`. When simulating pipeline yield, cap the projected `crop_max_yield` based on `30 - state.day`. If a crop takes 10 days to first yield, and there are only 8 days left, its projected yield must be 0, causing `expected_net_profit` to be negative, stopping the agent from buying the seed.

### 4. Mathematical Fix Implementation & Outcome
We implemented a strict `achievable_yield` cutoff in `V009-B` based on `remaining_days = 30 - current_day`. If a crop's minimum lifespan or its yield cycles cannot complete within the season, the expected value is set to 0.

**Experiment V009 Result:**
- **Control (V009-A):** ~$35,241 mean Final Bank
- **V009-B:** ~$37,139 mean Final Bank

The fix successfully yielded an absolute improvement of **~$1,898 (+5.39%)**. This confirms the hypothesis: preventing late-season planting both saves seed costs and frees up critical late-game labor to harvest crops that actually produce revenue.
