# Hypothesis 001: Step-72 Public-State Route Branch

## Hypothesis Statement
"Adding a step-72 route branch to V057, conditioned on the public shop signature and opponent animal count, will improve head-to-head win score against diverse opponents by enabling mid-game production pivots."

## Rationale

### Observed Gap (from EXTERNAL_3000_GAP_MATRIX.md)
V057 diverges from 3000+ strategies at **Day 12-15** (steps 288-360). The root cause: V057 commits to a fixed production route (cow-heavy) at game start and never re-evaluates. By Day 12, the first batch of shops has unlocked (every 3 days = Day 3, 6, 9, 12), and the market has begun to shift based on opponent production. 3000+ agents observe this public state and branch their macro-plan accordingly.

### Evidence from Public Strategies
1. **Kaito Fukami (3090.1)**: Uses "strict-future" mechanism — a hardcoded trajectory with conditional branches at specific steps. The v27 "midgame meta reset" explicitly re-evaluates the plan.
2. **COK-ZhangZiliang**: Implements a "step-72 public-state branch" and "route locking" — exactly the mechanism we're missing.
3. **Sellesta Research Notes**: N16 compatibility graph, N17 switch checkpoints, N28 mixture policies — all describe safe mid-game pivoting without breaking existing production.

### Mechanism
At step 72 (end of Day 3, first shop unlock):
1. Read `obs["town"]["unlocked_shops"]` to identify the shop signature.
2. Read `obs["farms"][1-player]["tiles"]` to count opponent pastures/coops.
3. Select one of 3-4 pre-defined route continuations:
   - **Route A (Cow-Heavy)**: If shops demand milk/wool and opponent has few animals → continue current V057 default.
   - **Route B (Crop-Pivot)**: If shops demand produce (strawberry/melon) and market inventory is low → shift labor from animal care to crop planting.
   - **Route C (Balanced)**: If shop draw is mixed → hedge between animals and premium crops.
   - **Route D (Defensive)**: If opponent is heavily invested in the same route → diversify to avoid mutual price crashes.

### Predicted Effect
- Win rate improvement of 5-15% against diverse opponents (measured on VALIDATION pool).
- Minimal downside risk because Route A is the current V057 default — the branch only activates when evidence suggests a better alternative.

### Test Plan
1. Implement the branch in a candidate `v113_route_branch.py`.
2. Test on DISCOVERY pool (seeds 10000-10063) first.
3. If win_score > 55% vs V057, advance to VALIDATION pool (seeds 11000-11063).
4. If validation passes (CI lower bound > 50%), advance to PROMOTION pool (seeds 12000-12127).
5. Keep/Revert based on PROMOTION result.

### Competing Hypothesis (must also test)
"V057 is production-limited, not market-limited. Adding more efficient labor scheduling (reducing idle movement) would improve results more than route branching."

This is the MARKET-LIMITED vs PRODUCTION-LIMITED comparison from the user's requirements. Both hypotheses should be tested independently on disjoint discovery seeds.

## Status
PROPOSED — awaiting corrected benchmark results to confirm V057's baseline before implementing.
