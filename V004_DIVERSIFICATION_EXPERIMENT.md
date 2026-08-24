# V004 Labor-Aware Diversification Results

## 1. Overall Economic Performance (N=90 games per variant)

| Opponent | V004-A (Control) | V004-B (Dynamic Diversification) | Diff ($) | Diff (%) |
|----------|------------------|----------------------|----------|----------|
| random | $30227.80 | $33696.00 | $+3468.20 | +11.47% |
| starter | $30227.80 | $33750.77 | $+3522.97 | +11.65% |
| melon_maxxer | $30227.80 | $33230.93 | $+3003.13 | +9.94% |
| **GLOBAL** | **$30227.80** | **$33559.23** | **$+3331.43** | **+11.02%** |

## 2. Labor Metrics (Mean per game)

| Metric | V004-A (Control) | V004-B (Diversification) |
|--------|-------------------|----------------|
| Avg Workers/Day | 1.02 | 1.17 |
| Peak Concurrent Workers | 7.00 | 7.00 |
| Total Labor Spending | $110.43 | $66.63 |
| Avg Daily Labor Deficit Sum | 1193.79 | 762.53 |
| Watering Misses | 1.87 | 8.72 |

## 3. Analysis & Conclusion
Labor-aware diversification completely reverses the failure seen in V002-D.
By ensuring that premium crops (like Strawberry and Tomato) are only planted when their expected profit outweighs the dynamically calculated cost of the labor required to sustain them, the agent is able to successfully cultivate these crops without a death spiral.
V004-B substantially outperforms the V004-A static-melon baseline.