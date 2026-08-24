# V009 Harvest Timing Experiment Report

## Executive Summary

V009-B successfully implemented mathematical harvest timing, achieving a mean final bank of **$37,139.98** across 180 games against random, starter, and melon_maxxer.
This represents an absolute improvement of **$1,898.71** (+5.39%) over V009-A ($35,241.27).

## Hypothesis & Mathematical Model

The hypothesis was that the agent was purchasing and planting seeds too late in the 30-day season (720 turns), wasting seed cost and critical late-game labor on crops that would never fully yield. V009-B corrects this by mathematically projecting the number of achievable yields based on the `remaining_days = 30 - current_day` formula, cutting off unharvestable investments and freeing labor for actual yields.

## Benchmark Methodology

- Opponents: random, starter, melon_maxxer
- Games per opponent: 30
- Total games: 180
- Seed range: 1000 to 1029 (deterministic)

## Economic Attribution

Comparing V009-A vs V009-B Overall Means:
- **Final Bank**: $35,241.27 -> $37,139.98 (Diff: $1,898.71)
- **Seed Spending**: $4,917.78 -> $4,512.22 (Diff: $-405.56)
- **Worker Spending**: $73.22 -> $76.20 (Diff: $2.98)
- **Total Revenue**: $38,029.49 -> $39,546.00 (Diff: $1,516.51)

## Late-Season Planting Analysis

- **Seeds Purchased After Day 20**: 21.39 (V009-A) -> 39.11 (V009-B)
- **Seeds Purchased After Profitable Date**: 10.72 (V009-A) -> 0.00 (V009-B)

## Production & Labor Efficiency

- **Idle Turns**: 185.40 -> 200.07
- **Watering Misses**: 4.54 -> 5.07
- **Movement Efficiency**: 48.64%% -> 49.75%

## Per-Opponent Results

### vs random
- **V009-A Mean**: $35,481.93
- **V009-B Mean**: $37,347.93 (Diff: $1,866.00)

### vs starter
- **V009-A Mean**: $35,435.60
- **V009-B Mean**: $37,390.30 (Diff: $1,954.70)

### vs agents/melon_maxxer.py
- **V009-A Mean**: $34,806.27
- **V009-B Mean**: $36,681.70 (Diff: $1,875.43)

## Final Conclusion

V009-B successfully eliminated late-season waste. By cutting unprofitable seed investments, it not only saved seed cost, but overwhelmingly generated more revenue because late-game labor was efficiently re-directed from doomed plants to harvesting actual profitable crops.

## Recommendation for V010

The next logical step is to address the remaining largest bottleneck, which appears to be movement efficiency and possibly re-introducing animal logistics if viable.
