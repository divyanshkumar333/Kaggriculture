# Hypothesis 008: 7-Step Front-Running Lookahead with Ranked Sell Slots

## Hypothesis
If 6-step front-running lookahead achieved a 97.0% win rate against 5-step with +$1,482 net margin, extending lookahead to 7 steps ($t+1 \dots t+7$) will continue to pull future sales forward to earlier slots, securing even earlier market depth before opponent order execution.

## Implementation Details
- Horizon $H=7$: Scan planned replay sell orders up to $t+7$.
- Available shed inventory is matched against debt from previous front-running steps.
- Sell slots are re-ranked using quadratic/linear marginal price impact.
- Exact debt repayment tracking ensures no double-selling or inventory starvation.

## Result
- Tested in EXP-013: 100 paired fresh seeds (200 matches across both seats, seeds 4000-4099).
- Opponent: V034_Champion (6-step lookahead).
- Match Record: 195W / 5L / 0T (**97.5% Win Rate**).
- Paired Record: 100W / 0L / 0T (**100.0% Win Rate**).
- Mean Paired Delta: **+$3,694**.
- Mean Cash: $90,709 vs $88,862 (Net Delta: **+$1,847/match**).
- Robustness: 0 errors, 0 timeouts, 0 illegal actions.
- Status: **PROMOTED TO CHAMPION (V035)**.
