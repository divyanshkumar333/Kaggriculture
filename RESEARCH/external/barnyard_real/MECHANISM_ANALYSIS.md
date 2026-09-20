# Barnyard Economist Mechanism Analysis

## Overview
This document analyzes the actual `main.py` extracted from the public Kaggle artifact `romanrozen/strong-barnyard-economist`.

## The "Queue-Aware" Myth
The public documentation (`INDEX.md`) claimed that Barnyard used queue-aware task scheduling and a production atlas to dynamically assign workers. **This is false.**
The actual code (`strong-barnyard-economist`) relies purely on a pre-recorded trace (`_ACTIONS`), identical in structure to V057 and Kaito. There is no queue, no production atlas, and no dynamic worker assignment other than standard `_weed_repair_action`.

## The "Turn 600 Sell-All" Myth
`INDEX.md` claimed Barnyard liquidated at turn 600.
The actual code only triggers `_terminal_liquidation` at **turn 716**. It carefully sells un-planned inventory across turns 716-717, and completely dumps everything at turn 718.

## The True Innovation: Clone Preemption (`_preempt_shift`)
Barnyard's core mechanism for winning is explicitly detecting if the opponent is playing a highly similar trace (a "clone"), and then front-running *itself*.
1. **Clone Detection**: Computes a `_public_signature` (count of workers, land, plants, animals) for both farms. If the `_clone_distance(obs)` is <= 6, it considers the opponent a clone.
2. **Premium Preemption**: Between turns 120 and 680, if facing a clone, it looks ahead 1 to 3 turns in its *own* trace. If it finds a planned sale of a premium good (Strawberry, Melon, Milk, Wool) that has a high market price, it pulls that sale forward to the current turn.
3. **Debt Repayment (`_repay_shift`)**: It logs the preempted quantity in `_SHIFT_STATE`. When the trace finally reaches the original turn of the sale, `_repay_shift` reduces the sale quantity to exactly balance the books.

## Demand-Aware Market Ranking
Like Kaito v27, Barnyard ranks sell slots using `_order_score` which includes a `_demand_per_day` multiplier, shifting sales away from saturated markets and towards items the town is rapidly consuming.

## Conclusion
Barnyard is an "Adaptive Preemptor". It wins the mirror match (or near-mirror matches against other trace-replay agents) by mathematically proving clone similarity and pulling premium sales forward to dump the market price exactly 1-3 turns before the opponent executes the identical sale.
