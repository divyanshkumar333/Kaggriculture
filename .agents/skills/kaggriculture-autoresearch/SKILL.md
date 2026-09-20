---
name: kaggriculture-autoresearch
description: Persistent autoresearch loop for Kaggriculture competition. Manages champion state, runs experiments, keeps/reverts candidates, persists lessons.
---

# Kaggriculture Autoresearch Loop

## Loop Protocol

READ -> RESEARCH -> HYPOTHESIS -> MODIFY -> COMMIT -> VERIFY -> GUARD -> KEEP/REVERT -> LOG -> LEARN -> REPEAT

## State Files (always read at cycle start)

- RESEARCH/CURRENT_CHAMPION.json
- RESEARCH/STATE.json
- RESEARCH/LESSONS.md
- RESEARCH/meta/current_meta.json
- RESEARCH/meta/strategy_families.json
- RESEARCH/experiment_log.md
- reports/LATEST_STATUS.md

## Benchmark Gates

SMOKE: 8-16 paired seeds (both seats), sequential runner
VALIDATION: 32-64 paired seeds
PROMOTION: 128+ paired seeds where compute allows

Use .venv\Scripts\python.exe for all runs.
Sequential execution always: avoid multiprocessing until environment is validated.

## Champion Promotion Rules

- Champion cannot change without PROMOTION benchmark passing
- Both seats required for all benchmarks
- Never destroy previous champion file
- Git commit every accepted improvement
- Git revert every rejected improvement

## Anti-Goodhart Rules

- Never weaken tests
- Never reduce seed count because candidate performs poorly
- Never remove adversaries
- Never change metric to make candidate win
- Never call analytical estimate a benchmark result

## Hypothesis Selection

Calculate for each candidate:
  EXPECTED_IMPACT * EVIDENCE_STRENGTH * TRANSFERABILITY / COMPUTE_COST

Select highest-value unresolved hypothesis.

## Required Files to Maintain

- RESEARCH/CURRENT_CHAMPION.json
- RESEARCH/LESSONS.md
- RESEARCH/meta/strategy_families.json
- reports/LATEST_STATUS.md
