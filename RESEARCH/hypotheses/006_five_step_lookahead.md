# Hypothesis 006: 5-Step Front-Running Lookahead with Ranked Sell Slots

## Hypothesis
If 4-step front-running lookahead achieved a 100% win rate against 3-step with +$2,088 net margin, extending lookahead to 5 steps ($t+1 \dots t+5$) may capture even earlier front-running opportunities for produce approaching harvest/delivery.

## Implementation Details
- Horizon $H=5$: Scan planned replay sell orders up to $t+5$.
- Available shed inventory is matched against debt from previous front-running steps.
- Sell slots are re-ranked using quadratic/linear marginal price impact.
- Exact debt repayment tracking ensures no double-selling or inventory starvation.

## Result
- Tested in EXP-011: 100 paired fresh seeds (200 matches across both seats, seeds 2000-2099).
- Opponent: V032_Champion (4-step lookahead).
- Match Record: 196W / 4L / 0T (**98.0% Win Rate**).
- Paired Record: 100W / 0L / 0T (**100.0% Win Rate**).
- Mean Paired Delta: **+$3,334**.
- Mean Cash: $88,309 vs $86,642 (Net Delta: **+$1,667/match**).
- Robustness: 0 errors, 0 timeouts, 0 illegal actions.
- Status: **PROMOTED TO CHAMPION (V033)**.
