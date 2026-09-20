# Barnyard Economist vs V057: Code-Level Analysis

## Overview
This document reconstructs the core architectural differences between our local champion `V057` and the public 3034.8 artifact `Barnyard Economist` (by Roman Rozen).

## 1. Action Structure & Task Scheduling
- **V057**: Uses deterministic index-based assignment. Each farm hand gets an action exactly according to their index in the `_ACTIONS` trace. If the trace says the 3rd farm hand digs, the 3rd hand digs, irrespective of position.
- **Barnyard Economist**: Implements **Queue-aware farming**. Tasks are placed in a queue and sorted by deadline (e.g., plant watering has a strict end-of-day deadline to prevent weed decay). Workers are assigned tasks dynamically via priority rather than fixed assignment.

## 2. Production Atlas
- **V057**: Does not compute global yield expectations; it just executes the trace.
- **Barnyard Economist**: Uses a **Production atlas**, meaning it pre-computes the yield schedules of all crops and animals on the board to accurately predict its inventory trajectory without simulating the full game forward.

## 3. Decision-Edge Logic
- **V057**: Re-evaluates front-running and weed-repair every single turn.
- **Barnyard Economist**: Only acts on information *changes* (decision edges). If no state variance has occurred, it executes the existing route without recomputing.

## 4. Terminal Behavior
- **V057**: Has no explicit terminal logic; relies on the trace to stop planting or buying cows.
- **Barnyard Economist**: Implements an **explicit sell-all sequence starting around turn 600**. It liquidates the entire shed and stops all long-horizon purchases, transitioning workers purely into short-horizon harvest/sell loops.

## Summary Gap
V057 lacks deadline-aware scheduling (relying instead on trace fidelity) and explicit terminal behavior. Barnyard Economist achieves its high score by perfectly optimizing worker utilization via queues and aggressively dumping inventory in the final 120 turns to maximize terminal bank.
