# Kaito Fukami (v27) vs V057: Code-Level Analysis

## Overview
This document reconstructs the core architectural differences between our local champion `V057` and the public 3090.1 artifact `Kaito Fukami v27 (Strict-Future / Midgame Meta Reset)`.

## 1. Action Structure & Route Strategy
- **V057**: Hardcodes the entire 720-step action sequence as a JSON array (`_ACTIONS`), effectively "memorizing" a specific optimized route (the trace). It adjusts dynamically only for weed repair and market front-running.
- **Kaito v27**: Uses a **Strict-Future constraint**. It does not allow peeking ahead into a pre-computed macro-route to determine when to sell. Instead, the route strategy is generated dynamically or segmented into verifiable epochs.

## 2. Market Ordering & Price Impact
- **V057**: Implements `_rank_sell_slots(obs, action)` which calculates `quantity * (current_quote - later_quote)` to prioritize the sales that cause the largest price impact.
- **Kaito v27**: Uses an identical price-impact ordering mechanism (as noted in `INDEX.md`), meaning the market-sale logic is functionally at parity.

## 3. Strict-Future Mechanism
- **V057**: `_future_target()` sweeps forward up to 30 steps into `_ACTIONS` to see if *we* plan to sell an item, and pulls it forward if the opponent is holding it.
- **Kaito v27**: Evaluates *purely on observable state*. It tracks opponent harvests and current shop states to predict opponent sales, triggering front-running without referencing its own "future" trace.

## 4. Branch Conditions & Meta Reset
- **V057**: Never aborts its core macro. If the market crashes, it stubbornly continues executing the trace, hoping to recover via dynamic market ranking.
- **Kaito v27**: Implements a **Midgame Meta Reset** (typically around turn 360). It evaluates whether the current route (e.g., cow scaling) is still optimal given the market inventory. If the milk market is saturated (I > I0), it forces a structural branch, halting cow purchases and liquidating assets or switching to crops.

## 5. Terminal Behavior & Fallback
- **V057**: Relies on the trace to naturally wind down.
- **Kaito v27**: Enforces a strict order-slot safety (max 10 market orders) and periodically re-evaluates the macro route, ensuring that terminal liquidation starts exactly when required by the remaining step count, rather than being hardcoded.

## Summary Gap
V057 is highly optimized for a static route and wins locally by dynamically perturbing it (front-running). Kaito v27 sacrifices some of that static optimality to gain **adaptability** via structural branching and the Midgame Meta Reset, which is likely why it achieves 3090.1 against the diverse public meta.
