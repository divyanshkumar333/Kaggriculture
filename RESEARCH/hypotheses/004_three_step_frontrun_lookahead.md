# Hypothesis 004: Three-Step Front-Running Horizon Expansion

## Date
2026-09-11

## Hypothesis
Extending the front-running lookahead window to 3 steps (`step + 1`, `step + 2`, `step + 3`) allows the agent to pull planned sales from up to 3 turns ahead when intermediate turns have no scheduled sales, securing even earlier market priority.

## Implementation
- Candidate: `agents/v031_v16_lookahead3.py`
- Searches `offsets = (1, 2, 3)` sequentially for the nearest future step with planned sales.
- Records repayment obligation on the exact target future step.
- Retains V029 price-impact order ranking and V16 weed repair.

## Benchmark Results vs V030_Champion (100 Paired Seeds = 200 Matches)
- **Match Record:** 198 Wins, 2 Losses, 0 Ties (**99.0% Match Win Rate**).
- **Paired Record:** 100 Wins, 0 Losses, 0 Ties (**100.0% Paired Win Rate**).
- **Mean Paired Delta:** **+$3,574**.
- **Mean Cash:** V031: $90,662 vs V030: $88,874 (**Net: +$1,787/match**).
- **Median Cash:** V031: $87,080 vs V030: $85,312.
- **Failures:** 0 errors across 200 matches.

## Conclusion
Hypothesis CONFIRMED with unprecedented 99.0% win rate across 200 matches.
Promoted to NEW CHAMPION.
