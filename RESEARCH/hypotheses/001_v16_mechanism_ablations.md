# Hypothesis 001: Forensic Decomposition and Causal Validation of V16-RC5

## Date
2026-09-11

## Hypotheses
1. **H1.1 (Front-Running)**: Moving next-turn scheduled sales of premium products (`MELON`, `MILK`, `STRAWBERRY`, `WOOL`) forward by 1 turn when current town demand is 0 provides queue priority and higher realized market price.
2. **H1.2 (Weed Repair)**: Bounded weed digging + 8-step replay alignment prevents state drift on seeds where random weeds block pastures/plantings.
3. **H1.3 (Repay Scheduling)**: Deducting front-run quantities from step $T+1$ planned orders prevents double-selling and preserves critical working inventory.
4. **H1.4 (Naive Dumping Rejection)**: Dumping all shed stock on turn with 0 town demand (tested in V033) will crash market prices and cause inventory starvation.

## Experimental Setup
- **Harness:** Multiprocessing paired-seed simulator (`tournament_harness.py`).
- **Seeds:** 100 paired fresh seeds (seeds 1000–1099), 200 matches per tournament across both seats.
- **Opponent:** Full V16-RC5 (`agents/public_v16_rc5.py`).

## Results

| Candidate / Ablation | Opponent | Matches | Match W-L-T | Match Win % | Paired Win % | Net Mean Delta | Mean Cash (Cand vs Opp) |
|---|---|---|---|---|---|---|---|
| **V16_Full** | V27_Public | 200 | 200 - 0 - 0 | **100.0%** | **100.0%** | **+$17,292** | $94,525 vs $77,233 |
| **V033 (Naive Dump)** | V16_Full | 200 | 30 - 169 - 1 | 15.0% | 7.0% | -$566 | $90,190 vs $90,756 |
| **V16_NoFrontRun** | V16_Full | 200 | 0 - 200 - 0 | **0.0%** | **0.0%** | **-$1,981** | $89,902 vs $91,883 |
| **V16_NoWeedRepair** | V16_Full | 200 | 32 - 85 - 83 | 16.0% | 3.0% | **-$858** | $90,574 vs $91,431 |
| **V16_NoRepay** | V16_Full | 200 | 27 - 173 - 0 | 13.5% | 5.0% | **-$553** | $90,293 vs $90,846 |

## Verdicts
- **H1.1 CONFIRMED:** Stateful front-running yields 200-0 clean dominance (+ $1,981/match).
- **H1.2 CONFIRMED:** Weed repair rescues corrupted seeds (+ $858/match).
- **H1.3 CONFIRMED:** Repayment avoids double-selling disruption (+ $553/match).
- **H1.4 CONFIRMED:** Uncalibrated dumping collapses price and fails (15% win rate).
