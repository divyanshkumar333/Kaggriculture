# Hypothesis 002: Dynamic Price-Impact SELL Slot Ordering

## Date
2026-09-11

## Hypothesis
Market orders submitted within a single turn are executed sequentially in order slots 0..9. For each player, the price received for a `SELL` order depends on current market inventory when that slot is processed. Reordering existing `SELL` orders within the turn so that products with highest price sensitivity (e.g. MELON with quadratic decay, STRAWBERRY with steep linear decay) execute in earlier slots will capture higher marginal prices before subsequent orders depress market depth.

## Implementation
- Candidate: `agents/v029_v16_impact_ranked.py`
- Preserves all planned quantities, front-running, weed repair, and repay logic without modification.
- Evaluates `_impact_score = quantity * max(0.0, current_price - future_price)`.
- Sorts only the existing `SELL` order slots in descending order of impact score.

## Benchmark Results vs V16-RC5 (100 Paired Seeds = 200 Matches)
- **Match Record:** 189 Wins, 11 Losses, 0 Ties (**94.5% Match Win Rate**).
- **Paired Record:** 100 Wins, 0 Losses, 0 Ties (**100.0% Paired Win Rate**).
- **Mean Paired Delta:** **+$1,783**.
- **Mean Cash:** V029: $91,367 vs V16: $90,476 (**Net: +$891/match**).
- **Median Cash:** V029: $87,975 vs V16: $86,957.
- **Failures:** 0 errors across 200 matches.

## Conclusion
Hypothesis CONFIRMED. Clean price-impact order ranking consistently extracts additional cash on virtually every seed without introducing any execution risk.
Promoted to NEW CHAMPION.
