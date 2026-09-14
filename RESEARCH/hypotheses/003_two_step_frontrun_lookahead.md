# Hypothesis 003: Multi-Step Front-Running Lookahead & Multi-Step Repayment

## Date
2026-09-11

## Hypothesis
V16-RC5 and V029 only check `step + 1` for planned sales. If `step + 1` has zero scheduled sales for an item, but `step + 2` has a planned sale and the shed currently holds unreserved stock, front-running that sale forward into `step` will secure an even earlier market queue position and capture higher prices before subsequent market saturation.

## Implementation
- Candidate: `agents/v030_v16_lookahead2.py`
- Implements `_future_target(step, item)` which checks step + 1, and if quantity is 0, checks step + 2.
- Employs a multi-step repayment schedule `state["due"][target_step]` to guarantee precise debt settlement on the exact target step, preventing double-selling.
- Retains V029's clean price-impact SELL slot ordering and V16's weed repair.

## Benchmark Results vs V029_Champion (100 Paired Seeds = 200 Matches)
- **Match Record:** 188 Wins, 12 Losses, 0 Ties (**94.0% Match Win Rate**).
- **Paired Record:** 100 Wins, 0 Losses, 0 Ties (**100.0% Paired Win Rate**).
- **Mean Paired Delta:** **+$2,203**.
- **Mean Cash:** V030: $90,980 vs V029: $89,878 (**Net: +$1,102/match**).
- **Median Cash:** V030: $87,158 vs V029: $86,556.
- **Failures:** 0 errors across 200 matches.

## Conclusion
Hypothesis CONFIRMED with 100% paired win rate.
Promoted to NEW CHAMPION.
