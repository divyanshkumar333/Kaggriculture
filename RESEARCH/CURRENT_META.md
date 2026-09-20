# Current Kaggriculture Meta Research

## 1. 3000+ Strategies Overview
The current elite meta (2800–3200+ Elo) on Kaggle represents a shift away from pure heuristic or naive behavioral cloning toward **hierarchical hybrid agents**.
A top-tier 3000+ agent typically exhibits:
- **Optimal Day-0 Capital Allocation**: Near 100% capital utilization (e.g., leaving exactly $22) on high-leverage assets like cows, avoiding over-indexing on low-ROI early hires.
- **Dynamic Capacity Scaling**: Avoiding strict ceilings like "6 workers max" in favor of adaptive scaling. Elite agents push to 12+ workers to manage 40+ strawberry plants without suffering decay or weed overrun.
- **Market Squeeze Exploitation**: When the shared market floods with milk (driving the price down to the $1 floor), 3000+ agents pivot labor entirely to high-margin ongoing crops (Strawberries, Tomatoes) that retain intrinsic value due to market-capped buy rates.

## 2. Strict-Future & Branching Policies
Instead of hardcoding the entire game, modern agents use a strict-future observability constraint. They evaluate state at `t` and lock into a macro-route (e.g., Cow Rush, Strawberry Flywheel, Market Spoiling). 
- **Branching Policies**: Agents check environmental triggers (e.g., "Opponent owns > 5 cows") and branch into orthogonal strategies (e.g., "Starve the feed market" or "Dump milk").
- **Policy Portfolios**: No single deterministic policy survives adversarial pressure. The meta is transitioning to selecting from 4-8 specialized models based on the opening conditions and random seed.

## 3. Persistent Execution (Worker Allocation)
Worker execution has decoupled from overarching strategy. 
- **Strategy** dictates macro-goals (e.g., "Water 20 strawberries").
- **Execution** handles the micro (which worker moves where).
While Hungarian matching algorithms are popular in documentation, they are often computationally excessive. Elite agents rely on persistent multi-step task commitments, ensuring that a worker doesn't interrupt a transit to chase a marginally closer weed, which minimizes transit waste.

## 4. Market-Aware & Terminal Strategies
The Kaggle market operates dynamically:
- **Shop Reactivity**: Town shops unlock randomly every 3 days. Agents must detect `unlocked_shops` and hold specific inventory (e.g., eggs, wheat) for the shop window.
- **Terminal Liquidation**: With 72-120 turns remaining, the optimal policy ceases planting and pivots entirely to harvesting, feeding, and shedding. All livestock and non-essential tools are discarded to maximize the final cash readout.
