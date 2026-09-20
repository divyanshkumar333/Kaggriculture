# Current Public Meta (September 2026)

## 1. Top Public Strategies

### A. destbreso "X-ray your agent"
- **Source**: Public Notebook / Forum discussion
- **Strategy Type**: Analytic framework
- **Behavior**: Provides an action-stripe extraction tool that reconstructs agent trajectories at t=24, 72, 144, 200, 400. This is the foundation of our `agent_lineage_clusters.csv`.

### B. Kaito Fukami 3090.1 (strict-future / v27 Meta Reset)
- **Source**: Leaderboard profile / replay analysis
- **Known Rating**: 3090.1
- **Strategy Type**: Dynamic Cow Expansion Limit & Strawberry Pivot
- **Opening**: Rapidly acquire 2-3 cows.
- **Worker Profile**: 2 workers (D0) $\rightarrow$ 6 workers (D6) $\rightarrow$ 11+ workers (D12+).
- **Animals**: Capped strictly before the "Milk Glut Trap". No more cows after milk price crashes to $1 (or inventory > 60).
- **Crop Profile**: Heavy strawberry planting in Q3/Q4. 40+ strawberries planted leveraging the massive labor pool originally bought with milk profits.
- **Terminal Behavior**: Liquidate cows in the final 50 turns. Cease planting.

### C. Yusuke Hayashi shop-router / three-day shop research
- **Source**: Forum discussion
- **Known Rating**: ~2950
- **Strategy Type**: Shop Reactivity
- **Behavior**: Modest, route-compatible production pivots based on shop unlocks.
- **Shop Behavior**: When a heavy demand shop unlocks (e.g., ICE_CREAM-heavy or BAKERY-heavy), marginal capital shifts slightly (e.g., planting an extra 4 wheat or feeding an extra cow) to meet the shop's periodic 1x demand, securing $15+ over market floor.

## 2. Live Meta Analysis
Recent high-rating episodes (>2900) universally exploit the **Milk Glut Trap**. 
Any agent (like `V025-A`) that runs a single, unbroken macro-policy (buying cows continuously) inevitably crashes into a $1 milk market while starving its own labor force. 
The live meta uses a **Branch Point**:
- **COW_RUSH**: Turn 0 to ~200. Maximize cow acquisition.
- **STRAWBERRY_PIVOT**: Turn 200+. When milk hits $1, freeze cow purchases. Divert 100% of marginal capital to HIRE and PLANT STRAWBERRY.

## 3. Worker Distribution (3000+ League)
- **Day 0**: 1 worker (Farmer only) or 2 workers.
- **Day 6**: 5-7 workers.
- **Day 12+**: 10-14 workers. (Median: 11).
*Conclusion: The previous repository assumption of a strict 6-worker ceiling is fatally flawed and mathematically countered by the Strawberry Pivot.*
