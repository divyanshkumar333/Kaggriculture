# Post-V104 Forensic & 2000+ Escalation Cycle Report

## 1. Executive Summary & Objective

**Primary Objective**: Drive towards **2000+ Actual Kaggle Rating** (escalating to 2500+, 3000+) using the 2945-farm chassis (`agents/the_2945_farm.py`).
**Milestone Honesty Policy**: Local tournament results (including 44W / 0L / 6D) are strictly local benchmarks and do NOT constitute a claimed Kaggle rating milestone until verified on the Kaggle public ladder.

---

## 2. Forensic Audit Results

### Task 1: Engine Integrity Audit
- **Verification**: Byte-for-byte SHA256 comparison between local `.venv` environment and the official PyPI wheel `kaggle_environments-1.32.7-py3-none-any.whl`.
- **Result**: Official SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` restored cleanly. Mismatch was purely Windows CRLF line endings. All simulator modifications reverted.
- **Documentation**: Certified in `RESEARCH/kaggle_loop/engine_integrity.md`.

### Task 2: V104 Kaggle Forensics
- **API Audit**: Checked `kaggle.api.competition_submissions('kaggriculture')`.
- **Finding**: While `submission_v104_quote_priority.tar.gz` had been packaged locally at commit `2b3a7c1`, it had **never been submitted to Kaggle**.
- **Active Submissions Prior to this Cycle**:
  - Slot 1: `56403931` (V058 Generalized Spoiler, rating 954.7, 95 episodes)
  - Slot 2: `56403913` (V057 Control, rating 901.6, 93 episodes)
- **Local Record Clarification**: The reported 44W / 0L / 6D record is 100% local tournament data across the legacy bot pool.

### Task 3: Causal Validation (V104 Quote Priority vs Control)
- **Diff Analysis**: `agents/v104_quote_priority.py` differs from `agents/the_2945_farm.py` by exactly ONE line: removal of `if len({o[1] for o in block}) == len(block):` in `_r37_reorder_sales` (line 1838).
- **Execution Trace**: In seed 42, Quote Priority reorders sales 26 times vs Control's 19 times (+7 reordered turns).
- **Rigorous Sequential Validation** (Seed-paired, dual-seat):
  - **H2H (Quote Priority vs Control, 16 matches)**:
    - Quote Priority: **6 Wins (37.5%)**
    - Control (2945): **0 Wins (0.0%)**
    - Draws: **10 Draws (62.5%)**
    - Losses: **0 Losses (0.0%)** — Pareto-superior, strictly zero regressions.
  - **Population (Quote Priority vs V057 and V16, 16 matches per agent)**:
    - V104 Control: 16W - 0L - 0D (100.0%) | Mean Cash: $107,413
    - V104 Quote Priority: 16W - 0L - 0D (100.0%) | Mean Cash: $107,413
- **Certification**: Documented in `RESEARCH/kaggle_loop/causal_validation_v104.json`.

---

## 3. Market Mechanics Laboratory Findings

Using the official byte-for-byte engine, controlled experiments revealed:

1. **Premium Lead Edge**: In contiguous order slots, leading with Strawberry over Wheat generates **+$131.00 (+6.4%)** in a single turn on 10 strawberries.
2. **Chunking Hazard**: Splitting 10 strawberries across two 5-unit orders costs **-$49.00 (-4.7%)** because later units sell into depressed prices in Slot 1.
3. **Duplicate-Commodity Gating Penalty**: When duplicate commodities exist in an unsorted block, the 2945 chassis failed to sort, suffering a **-$186.00 (-13.8%)** penalty in a single wave. V104 completely cures this.
4. **Price Collapse Hierarchy**:
   - `STRAWBERRY`: -67.9% cliff (Quadratic decay)
   - `MILK`: -61.2% cliff (Quadratic decay)
   - `WOOL`: -60.1% cliff (Quadratic decay)
   - `TOMATO`: -28.0% moderate decay
   - `CARROT`: -21.7% linear decay
   - `MELON`: -13.1% slow decay (High base $250)
   - `EGG`: -12.6% stable sink
   - `WHEAT`: -12.4% staple buffer
   - `FERTILIZER`: -9.9% flat demand
5. **Optimal Sell Queue Rule**:
   `STRAWBERRY > MILK > WOOL > MELON > TOMATO > CARROT > EGG > WHEAT > FERTILIZER`.

---

## 4. Economic Ablation & Reversion

### Care Gating Audit:
- In `kaggriculture.py` line 829, `pending_care_bonus` is ONLY incremented if `tile["cared_today"] and tile["fed_today"]`.
- When an animal is unfed, `CARE` is discarded at midnight.
- Furthermore, on production days `min(max_held, yield + 1 + bonus)` clips bonuses when `yield + pending >= 5`.
- Audit revealed **24.9% of CARE actions in 2945 farm are WASTED** (13.1% unfed, 11.8% at cap).

### Tomato Unlocked (V105) Empirical Reversion:
- Tested hypothesis: Lowering tomato entry gate (`CROP_MIN_PRICE=58`, shop threshold < 1) to capture tomato revenue after Day 18.
- **Empirical H2H Benchmark vs V104** (12 matches across 6 seeds, dual-seat):
  - V105 (Tomato Unlocked): **0 Wins - 4 Losses - 8 Draws**
  - **Mean Cash Delta**: **-$1,230 regression** (Seed 101: -$3,578, Seed 123: -$3,802).
- **Root Cause**: Investing in tomatoes on Day 18 diverts $12k+ in capital and labor away from the high-margin animal/strawberry flywheel. The original author's conservative gate (`CROP_MIN_PRICE=70`, 3 shops) was economically protective.
- **Action**: **REVERTED**. V105 will not be submitted.

---

## 5. Kaggle Submission Telemetry

Following the single-challenger protocol without sacrificing both active slots:

- **Submitted Package**: `submission_v104_quote_priority.tar.gz`
- **Candidate Name**: `V104 Quote Priority`
- **Submission ID**: `56417252`
- **Target Slot**: Replaces weaker active slot `56403913` (V057 Control at 901.6 rating).
- **Preserved Slot**: `56403931` (V058 Generalized Spoiler at 954.7 rating).
- **Status**: Registered on Kaggle, awaiting leaderboard matchmaking.

---

## 6. Next Steps Towards 2000+ Rating

1. **Monitor Submission 56417252**: Track episode play and rating convergence on the Kaggle ladder.
2. **Next Challenger Development (V106)**:
   - Combine V104's market sorting fix with precision care-gating reflex (suppress CARE when unfed or at cap).
   - Test coalescing identical commodities within contiguous SELL blocks to eliminate multi-slot chunking penalties.
   - Rigorously gate all candidate changes behind paired seed benchmarks before any new submission.
