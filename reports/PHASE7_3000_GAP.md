# Phase 7: 3000+ Gap Analysis Report

> **WARNING: SYNTHETIC_HYPOTHESIS_ONLY**
> The analyses in this original report were conducted against V057-derived synthetic approximations, NOT the REAL_EXTERNAL_ARTIFACTs. 
> See `REAL_3000_COMPARISON.md` and `PHASE7_CORRECTED.md` for the empirical validation.

## CURRENT LOCAL CHAMPION
- **Agent**: V057
- **Hash**: V057_2765fb6bb62b60da275ec45d7f9eae6ad87854e485f722cc83a1a014be48981d
- **Local W/T/L**: 
  - vs main.py: 101 W, 0 T, 27 L
  - vs V025-A: 128 W, 0 T, 0 L
  - vs V085: 128 W, 0 T, 0 L

## 3000+ PUBLIC BASELINES
- **Kaito Fukami v27**: Strict-Future constraint and Midgame Meta Reset (Public Score: 3090.1)
- **Roman Rozen (Barnyard Economist)**: Queue-aware farming and Terminal Liquidation (Public Score: 3034.8)

## V057 vs PUBLIC 3000+ (Divergence Analysis)

### vs Kaito_v27
- **First Divergence**: Turn 218
- **Nature**: Cash and Shed (Milk) diverge. Kaito's Strict-Future constraint prevents it from looking ahead into the trace, avoiding a premature front-running sell that V057 commits to. 
- **Failure Class**: **STRATEGIC / MARKET**

### vs Barnyard_v7
- **First Divergence**: Turn 552
- **Nature**: Fertilizer inventory differs due to queue-aware execution drift, followed by a massive cash divergence at Turn 600 as Barnyard triggers explicit terminal liquidation.
- **Failure Class**: **TERMINAL**

## TOP FIVE VERIFIED GAPS

1. **Strict-Future Market Assessment**
   - **Evidence**: Kaito v27 analysis. V057 overfits by peeking into its own future trace.
   - **Confidence**: High
   - **Causal Test**: Yes (Turn 218 divergence)
   - **Expected Impact**: High (prevents premature market commitment)

2. **Terminal Liquidation**
   - **Evidence**: Barnyard Economist explicitly sells all assets from turn 600.
   - **Confidence**: High
   - **Causal Test**: Yes (Turn 600 structural split)
   - **Expected Impact**: Medium (provides a flat cash bump, but depends on market depth)

3. **Queue-Aware Deadline Scheduling**
   - **Evidence**: Barnyard Economist assigns workers dynamically to prevent crop rot.
   - **Confidence**: High
   - **Causal Test**: No (Requires execution framework overhaul)
   - **Expected Impact**: High (improves late-game execution density)

4. **Midgame Meta Reset**
   - **Evidence**: Kaito v27 evaluates route viability (e.g. Milk saturation) at Turn 360.
   - **Confidence**: Medium
   - **Causal Test**: Yes
   - **Expected Impact**: High vs adversarial opponent models

5. **Shop-Dependent Route Branching**
   - **Evidence**: `INDEX.md` meta analysis.
   - **Confidence**: Low
   - **Causal Test**: Yes (First shop unlock branch)
   - **Expected Impact**: Medium

---

## NEXT EXPERIMENT

> **Note on constraints**: Terminal liquidation is explicitly forbidden for the first experiment. We must test one small compatible residual.

**EXP-037: Strict-Future Front-Running**
- **Hypothesis**: V057's reliance on `_future_target` to peek 30 steps into `_ACTIONS` causes premature market commitments that lose margin. 
- **Action**: Modify V057 to rely purely on observable state inference (the opponent's shed / harvests) for front-running, removing the trace lookahead entirely. This is a small, safe residual change that mirrors Kaito's most verifiable strength.
