# Kaggriculture Milestone 1 & 2: Reliability & Local Benchmarking

This plan outlines the execution steps for fulfilling Phases 2 through 12, focusing on instrumenting the baseline agent, establishing the benchmarking suite, conducting failure analysis, and performing systematic optimization.

## Phase 1 (Completed)
`V001_AUDIT.md` has been successfully created. The primary blocker discovered is that hired farm hands currently idle and waste money.

## User Review Required
Before proceeding with the massive benchmarking and optimization sequence, please confirm the following technical implementation details for the framework upgrades:

## Phase 5: Economic Calculator Update & Pathfinding

### Pathfinding
- **Observation:** The game rules state that units can occupy the same space, and even locked tiles and structures (like coops/pastures) are passable. 
- **Ponytail principle:** Since the grid is fully passable without obstacles, the current greedy Manhattan distance routing (`step_toward`) already generates the mathematically optimal shortest path. A full BFS/A* graph search would add unnecessary complexity and latency with no change in output. 
- **Action:** I will leave `step_toward` as-is but add a `ponytail:` comment explaining why BFS was skipped.

### Exact Economics
- **Observation:** The agent currently assumes a hardcoded `price > 50` threshold and a generic `drop_factor` for pricing, causing it to overproduce melons into a crashed market and discard them when the shed fills.
- **Action:** I will implement the exact pricing functions specified in the README:
  - `price(inv) = base + sign * amp * f(|inv - I0|)`
  - Shape functions: `linear`, `sq`, `sqrt`, `log`, `hinge`
  - Constants for all resources (`base`, `T`, `below_func`, `below_target`, `above_func`, `above_target`)
- **Action:** I will update `EconomicCalculator.expected_sell_value(product, quantity)` to simulate the exact step-by-step price impact of a sell order, stopping the agent from selling when the marginal price falls to $1.

## Phase 6: A/B Strategy Testing

The failure analysis showed that V001 is a monoculture (Melons only) and fails to scale land or use animals. I will create two strategic variants to compete against `v001_baseline`:

### V001-A (Mixed Farm & Expansion)
- **Goal:** Diversify crops, utilize animals, and expand land to prevent market crashes.
- **Changes:**
  - Will track expected ROI across all crops/animals and plant the highest yield option.
  - Will buy the NE, SW, and SE quadrants when bank exceeds $3k, $6k, and $10k.
  - Will build Coops/Pastures and raise animals.

### V001-B (Aggressive Melon + Smart Market)
- **Goal:** Stick to the Melon meta but fix the shed bottleneck.
- **Changes:**
  - Will only plant Melons when the Melon price is > $100.
  - Will queue up to 10 sell orders per turn instead of 2.
  - Will stop harvesting Melons if the shed is full and price is at the floor, leaving them on the vine until the price recovers.

## User Review Required

> [!IMPORTANT]  
> 1. **Pathfinding**: Do you approve skipping BFS since the grid is obstacle-free and Manhattan routing is already optimal?
> 2. **Strategies**: Do you approve the V001-A and V001-B variant designs?

Once approved, I will implement the Economic Calculator in `v001_baseline.py` and create the A/B variants.

