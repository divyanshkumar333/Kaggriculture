# Hypothesis 007: 6-Step Front-Running Lookahead with Ranked Sell Slots

## Hypothesis
If 5-step front-running lookahead achieved a 98.0% win rate against 4-step with +$1,667 net margin, extending lookahead to 6 steps ($t+1 \dots t+6$) may capture additional margin, though margin expansion may begin to decelerate as the horizon spans well past town shop consumption intervals ($T_{shop} = 4$).

## Implementation Details
- Horizon $H=6$: Scan planned replay sell orders up to $t+6$.
- Available shed inventory is matched against debt from previous front-running steps.
- Sell slots are re-ranked using quadratic/linear marginal price impact.
- Exact debt repayment tracking ensures no double-selling or inventory starvation.

## Result
- Tested in EXP-012: 100 paired fresh seeds (200 matches across both seats, seeds 3000-3099).
- Opponent: V033_Champion (5-step lookahead).
- Match Record: 194W / 6L / 0T (**97.0% Win Rate**).
- Paired Record: 100W / 0L / 0T (**100.0% Win Rate**).
- Mean Paired Delta: **+$2,963**.
- Mean Cash: $90,143 vs $88,662 (Net Delta: **+$1,482/match**).
- Robustness: 0 errors, 0 timeouts, 0 illegal actions.
- Status: **PROMOTED TO CHAMPION (V034)**.
