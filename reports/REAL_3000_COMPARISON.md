# Real 3000+ Artifact Comparison

## Overview
This document outlines the first-divergence analysis and strategic comparison between the local champion (V057) and the two real public artifacts (Kaito v27 and Barnyard Economist).

## Base Trace Divergence
The previous assumption that Kaito and Barnyard shared a core trace with V057 up to the midgame (Turn 218/552) was based on synthetic, hallucinated artifacts. 

The **real** artifacts diverge from V057 at **Turn 1**.

### 1. The Opening Strategies
A direct script extraction of `_ACTIONS` / `_LEGACY_ACTIONS` reveals that the three agents use completely different opening playbooks (different root traces):

- **V057 (Local Champion)**: 
  - **Opening**: HIRE5
  - **First Move**: Farmer picks up 1 COW, 5 hands execute separate tasks.
- **Kaito v27**:
  - **Opening**: HIRE4
  - **First Move**: Farmer picks up 1 COW, 4 hands execute tasks. (The agent docstring confirms this: "HIRE4 opening became the dominant Top-30 prior").
- **Barnyard Economist**:
  - **Opening**: SHEEP-based
  - **First Move**: Farmer picks up 1 SHEEP.

Because they diverge structurally at Turn 1, they are not variations of the same trace. They are entirely distinct agricultural routes.

## Execution and Market Mechanics
While the underlying farming routes differ, the runtime code wrappers surrounding those routes reveal the true meta of the 3000+ bracket:

### 1. Market Sale Ranking (Shared by both 3000+ agents)
Both Kaito and Barnyard have discarded static price-impact scoring in favor of **Demand-Aware Scoring**. 
```python
demand = max(0.25, _demand_per_day(obs, configuration, item))
excess = max(0.0, current_inventory + quantity - 10000)
urgency = min(1.0, (excess / demand) / 10.0)
return score * (1.0 + _DEMAND_ALPHA * urgency)
```
This algorithm shifts sales dynamically towards items that the Town consumes fastest, rather than just items that have the lowest raw price drop.

### 2. The Fallacy of Front-Running (Kaito)
V057 uses a complex `_front_run` lookahead to try to beat opponents to the market. Kaito v27 proves this is unnecessary or even harmful: Kaito completely deleted the `_future_target` lookahead and simply relies on the demand-aware market ranking to sell optimally, scoring 3090.

### 3. Adaptive Preemption (Barnyard)
Barnyard *does* use front-running, but in a mathematically robust way:
1. It calculates `_clone_distance()` to prove if the opponent is running an identical (or near-identical) trace.
2. If and only if the opponent is a clone, it looks ahead into **its own trace** to pull premium sales (Strawberry, Melon, Milk, Wool) forward by 1-3 turns.
3. It keeps an exact ledger (`_SHIFT_STATE`) to repay the preempted quantity exactly on the turn it was originally scheduled.

## The Gap Matrix
The differences between V057 (~1100 level) and the 3000+ agents are now clear:

| Feature | V057 | Kaito v27 | Barnyard Economist |
| :--- | :--- | :--- | :--- |
| **Base Trace** | HIRE5 (Cow) | HIRE4 (Cow) | SHEEP |
| **Market Rank** | Static Impact | Demand-Aware | Demand-Aware |
| **Preemption** | Blind Lookahead | None | Exact Clone-Preempt |
| **Terminal Sell** | Turn 600? (Actually unused in base) | None explicit | Turn 716-718 |

## Conclusion
The gap to 3000+ is NOT a midgame branching failure. It is a fundamental difference in (a) the base farming trace (HIRE4 vs HIRE5 vs SHEEP), and (b) the market scoring algorithm (Demand-Aware vs Static). Barnyard adds a specialized clone-assassin mechanism on top.
