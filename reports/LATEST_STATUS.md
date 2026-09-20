# Kaggriculture Autoresearch Lab — Latest Status

**Updated:** 2026-09-20T09:35:00Z  
**Cycle:** 1 (Takeover & Audit)

---

## CURRENT CHAMPION

| Field | Value |
|---|---|
| Agent | `main.py` |
| Architecture | V032 Lookahead4 + Opponent Shed Inference + Front-Run + Repay + Impact Rank |
| Git Commit | 7998a1a (kaggle update) |
| Status | CHAMPION (frozen from prior session) |
| Verified vs v027 (smoke) | **8W/0T/0L** (2026-09-20, seeds 7700-7707, delta +$12,759) |
| Last Kaggle Score | UNKNOWN — not yet retrieved |
| Best Kaggle Score | UNKNOWN |

## CURRENT CANDIDATES

| Slot | Agent | Status |
|---|---|---|
| ACTIVE_A | `main.py` | CHAMPION |
| ACTIVE_B | `agents/v100_grandmaster_frontrun.py` | EXP-035 SMOKE RUNNING |

## KNOWN VULNERABILITIES

| Opponent | Win Rate | Source | Notes |
|---|---|---|---|
| public_v16_rc5 | 14.5% | EXP-030 (prior session) | Prisoner's Dilemma - both run same trace |
| v027_base | 100% | EXP-028, confirmed smoke 7700-7707 | Dominates |
| v025_a | 100% | EXP-029 (prior session) | Dominates |

## CURRENT META

- Top Kaggle agents: 3090+ (Kaito Fukami v27-v48 series)
- Meta shift: Real-time execution > static trace replay
- Our weakness: trace-locked to single game, fails vs trace-mirror

## TOP FAILURE MODE

**Prisoner's Dilemma vs V16 mirror:** Both agents share V16 trace. Front-run creates symmetric debt.
Main fix path: V100 real-time executor — benchmark in progress.

## TOP EXTERNAL DISCOVERY

Kaito Fukami "40/40 Early Floor | v48 Fast Routes" scores 3090.1.
Key difference from our approach: observable event branching (not single trace).

## LAST EXPERIMENT

**EXP-034 (prior session):** V052_Adaptive vs V025_A: 1000W/0L, +$18,420 mean delta.

## CURRENT EXPERIMENT

**EXP-035:** V100 (grandmaster real-time executor + front-run overlay) vs CHAMPION (main.py)
- Smoke test: 8 pairs, seeds 7800-7807
- Status: RUNNING

## NEXT EXPERIMENT (if EXP-035 fails)

Hypothesis EXP-036: Terminal controller — stop planting Day 25+, liquidate
Expected impact: +$3k-8k per game in close matches

## ACCEPTED IMPROVEMENTS (this session)

0 (audit/setup cycle only)

## REJECTED IMPROVEMENTS (this session)

0

## V099 AUDIT STATUS

V099 implementation does NOT match research claims.
V099 = V025-A + single cow count threshold. Not Bayesian.
See RESEARCH/V099_IMPLEMENTATION_AUDIT.md.
