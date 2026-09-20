# V099 Implementation Audit

**Date:** 2026-09-20
**Status:** COMPLETE

## Claims vs Reality

V099 (`agents/v099_adaptive_master.py`) claims to be a "Bayesian Adaptive Master".

| Claim | Implemented? | Evidence |
|---|---|---|
| imports family_classifier | NO | Only imports math, scipy |
| imports calibration | NO | Not in file |
| imports counter_policy | NO | Not in file |
| Eight-family posterior | NO | Only 2 classes via `opp_cows >= 3` |
| Calibrated probabilities | NO | Binary threshold only |
| Counterfactual rollouts | NO | No rollouts or simulation |
| Persistent policy state | NO | active_policy recomputed each call |
| Legal-only observations | PARTIAL | No strict-future guard |

## What V099 Actually Does

1. Day 0: Fixed hardcoded 7-melon, 5-wheat, 4-sheep, 2-hire
2. Day 1+: Cow scaling; if opp_cows >= 3 -> BERRY_FLYWHEEL else V097
3. Task dispatch: Hungarian matching (scipy) recalculated every turn
4. No opponent shed inference, no market residual, no terminal controller

V099 = V025-A + 1-bit threshold wrapper. NOT a Bayesian system.

## Missing Modules

- family_classifier.py: does not exist in repo
- calibration.py: does not exist in repo
- counter_policy.py: does not exist in repo

## Action

Do NOT patch the report. Patch the implementation.
Treat V099 as BASELINE until local benchmark validates it.

Actual champion: main.py (V032 lookahead, opponent-shed inference,
front-running, repay scheduling, impact ranking).
