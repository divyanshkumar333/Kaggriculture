# Benchmark Integrity Report

## The Flaw
The previous benchmark harness (`scripts/bench_paired.py`) contained a critical statistical flaw regarding its implementation of Common Random Numbers (CRN). Specifically, it evaluated Game 1 on `seed = S` and Game 2 on `seed = S + 1000000`. 

Adding an offset completely destroyed the paired variance reduction property of the CRN methodology. It was effectively running two independent games rather than evaluating both agents against identical market conditions, shop draws, and weed spawn rolls. Furthermore, the statistics averaged the cash outcomes of the two independent games before determining a win/loss, which fundamentally violates paired difference testing.

## The Correction
We have implemented **True Common-Random-Number Pairing**:
1. **Identical Seeds:** Both seats (A vs B, and B vs A) are now evaluated using the exact same random seed. No offset is added.
2. **Proper Aggregation:** The harness now treats the pair of games as two separate observations of win/loss/tie. For each block (seed S):
   - Seat 0: A vs B $\rightarrow$ Outcome $O_1$
   - Seat 1: B vs A $\rightarrow$ Outcome $O_2$
3. **Paired Bootstrap:** The bootstrap sampling now resamples *entire seed blocks* to compute the 95% Confidence Interval for both the win score and the mean cash delta. This preserves the paired correlation structure.
4. **Frozen Pools:** Seeds are now disjointly allocated into `DISCOVERY`, `VALIDATION`, and `PROMOTION` pools to prevent adaptive overfitting.

## Autoresearch Enforcement
The autoresearch loop is now strictly gated by this integrity standard. Candidate agents must pass this paired comparison over the validation seed pool. Overwriting of the champion is strictly blocked unless the paired bootstrap lower bound confirms superiority.

> [!CAUTION]
> Do NOT revert to `seed + 1000000` under any circumstances. Independent sampling drastically increases the variance of the performance estimator and leads to false positive promotions.
