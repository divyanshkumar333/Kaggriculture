# Hypothesis 009: 8-Step Front-Running Lookahead with Ranked Sell Slots

## Hypothesis
If 7-step front-running lookahead achieved a 97.5% win rate with +$1,847 net margin, extending lookahead to 8 steps ($t+1 \dots t+8$) matches the 8-turn farm hand harvest/delivery cycle ($\tau_{TSP} \approx 8$), allowing full pre-emption of worker deliveries to the shed before price drops.

## Implementation Details
- Horizon $H=8$: Scan planned replay sell orders up to $t+8$.
- Available shed inventory is matched against debt from previous front-running steps.
- Sell slots are re-ranked using quadratic/linear marginal price impact.
- Exact debt repayment tracking ensures no double-selling or inventory starvation.

## Result
- Tested in EXP-014: 100 paired fresh seeds (200 matches across both seats, seeds 5000-5099).
- Opponent: V035_Champion (7-step lookahead).
- Match Record: 198W / 2L / 0T (**99.0% Win Rate**).
- Paired Record: 100W / 0L / 0T (**100.0% Win Rate**).
- Mean Paired Delta: **+$3,981**.
- Mean Cash: $87,443 vs $85,453 (Net Delta: **+$1,990/match**).
- Robustness: 0 errors, 0 timeouts, 0 illegal actions.
- Status: **PROMOTED TO CHAMPION (V036)**.
