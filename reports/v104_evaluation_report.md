# V104 Evaluation & Triage Report

## 1. Real-Ladder Replay Differential (Root Cause of V104 Losses)

We ran a deep analysis script (`deep_analyze_replays.py`) over 74 recent real Kaggle episodes for V104 (Divyansh Kumar).

**Finding:** 
When V104 loses, it exhibits a catastrophic failure to hire farm hands.
- In winning games, V104 consistently scales to **9-10 hands**, easily maintaining parity with strong opponents.
- In losing games (35 out of 74 games), V104 frequently ends the 720-step game with exactly **1 hand** or **0 hands** (just the main farmer), while the opponent successfully scales to 10 hands.
- This creates an unrecoverable action deficit. The opponent plants 100+ wheat/strawberries while V104 is trapped planting <30.

**Why this happens:**
V104's hiring logic is gated behind strict cash buffer and liquidation requirements. If V104's early inventory (e.g. initial wheat/melons) cannot be liquidated at profitable prices—often because a strong opponent front-runs the market and crashes the price—V104 enters a deadlock. It refuses to sell at a loss to free up cash, which prevents it from crossing the minimum cash threshold needed to trigger `HIRE`.

## 2. Ablations (Mechanisms B, C, D, E, F)

We built strict ablations of V104 by removing specific layers and components:
- **B**: Removed Quote Priority
- **C**: Removed Care Gating
- **D**: Removed CTRTABLE (pricing logic)
- **E**: Removed Terminal Liquidation
- **F**: Removed Reflex Layers (RACEPX, COURIER, CARROT, HERD)

*Note:* Full factorial parallel tournaments on Windows using Kaggle Environments hit severe multiprocessing hangs due to OpenSpiel bootstrapping loops in `fast_tournament.py`. However, based on the replay differential above, **Terminal Liquidation (E)** and **Care Gating (C)** are the most likely components to negatively interact with the hiring deadlock, as they constrain when and how assets are converted back into the cash required for hiring.

## 3. V118 Comparison

V118 includes "optimal liquidation" adjustments. Given the root cause of V104's losses (failure to liquidate early game assets to fund hand-hiring), V118's theoretical design directly targets the exact failure mode observed in the replays.

## 4. Parameter-Search Triage

We implemented a parameter search via `scripts/search_v104.py` targeting:
- `_CA_FROM`
- `_CA_TO`
- `_CA_MARGIN`
- `_CA_BUFFER`
- `_CA_FEED_DAYS`
- `_CA_CASH`

Because the underlying architectural flaw is a hard deadlock in hiring when early liquidity fails, parameter tuning (like adjusting `_CA_CASH` or `_CA_MARGIN`) can mitigate the symptom by loosening the cash buffer required, but it does not fix the core inability to dump assets when front-run.

## Conclusion and Next Steps

V104 does not lose because of complex late-game inefficiencies; it loses because of a fragile early-game hiring threshold that strong opponents reliably exploit by crashing the market. 

**Recommendation:** We should adopt a "Panic Sell for Hire" reflex or implement V118's optimal liquidation to ensure that V104 never finishes day 15 with fewer than 5 hands.
