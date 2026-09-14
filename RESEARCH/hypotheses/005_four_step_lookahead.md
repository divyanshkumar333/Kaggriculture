# Hypothesis 005: 4-Step Front-Running Lookahead with Ranked Sell Slots

## Hypothesis
If 2-step and 3-step front-running lookaheads improved match win rates (94% and 99%) and net cash deltas (+$1,102 and +$1,787), extending the lookahead horizon to 4 steps ($t+1, t+2, t+3, t+4$) will allow the agent to pre-empt produce deliveries up to 4 turns before they reach the shed, securing higher market prices before opponent market orders crash the price.

## Implementation Details
- Horizon $H=4$: Scan planned replay sell orders up to $t+4$.
- Available shed inventory is matched against debt from previous front-running steps.
- Sell slots are re-ranked using quadratic/linear marginal price impact.
- Exact debt repayment tracking ensures no double-selling or inventory starvation.

## Result
- Tested in EXP-010: 100 paired fresh seeds (200 matches across both seats).
- Match Record: 200W / 0L / 0T (100.0% Win Rate).
- Paired Record: 100W / 0L / 0T (100.0% Win Rate).
- Mean Paired Delta: +$4,176.
- Mean Cash: $90,774.4 vs $88,686.4 (Net Delta: +$2,088.0/match).
- Failures: 0 errors, 0 timeouts, 0 illegal actions.
- Status: **PROMOTED TO CHAMPION (V032)**.
