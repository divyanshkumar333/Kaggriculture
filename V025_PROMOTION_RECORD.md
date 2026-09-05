# V025-A Promotion Record

**Status:** PROMOTION COMPLETE & VERIFIED  
**Candidate:** `agents/v025_a_aggressive_cows.py`  
**Target:** `main.py`  
**Timestamp:** `2026-09-05T06:17:11Z` (`2026-09-05 11:47:11 IST`)  
**Kaggle Submission Status:** **NO KAGGLE SUBMISSION OCCURRED** (Awaiting explicit approval)

---

## 1. SHA-256 Integrity Verification

| File / Component | Path | SHA-256 Checksum | Match Status |
| :--- | :--- | :--- | :--- |
| **Old `main.py` (Backup)** | `main_pre_v025a_promotion.py` | `56f2db7229cd2b290d24d6d38977a60d6bd6396317be6a4d3c87363777e03605` | Preserved (Immutable) |
| **Candidate Source** | `agents/v025_a_aggressive_cows.py` | `4eb096b363ff1ee0ffba6d2ed19a46f5653c09fc7142479a8a13297f3ae319b0` | Verified |
| **Promoted Target** | `main.py` | `4eb096b363ff1ee0ffba6d2ed19a46f5653c09fc7142479a8a13297f3ae319b0` | **100% Exact Match** |
| **Historical Control V023-G** | `agents/v023_g_capital_optimizer.py` | `55f4bdfdcff3be21a569f146c0071cbcd231725e567afec1761c620d7dbc4260` | Preserved (Immutable) |
| **Historical Control V022-C** | `agents/v022_c_market_batching.py` | `ee383738b5565300fb8c7d8d94827774820716c6b91a02b88ead856b7c00e0a1` | Preserved (Immutable) |
| **Historical Control V020-C** | `agents/v020_c_competitive_surgical.py` | `df58272f1752d8a1204275647947f10264a4341dc79450058296087aff27e457` | Preserved (Immutable) |

- **Syntax Compilation:** `py_compile.compile('main.py')` executed with zero errors.
- **Diff:** Byte-for-byte exact copy from candidate source into `main.py`.

---

## 2. Deterministic Smoke-Test Results

- **Environment:** `kaggriculture` (720 steps, episode seed 42)
- **Matchup:** `main.py` vs `random`
- **Result:**
  - `main.py` (P0) Reward: **$59,821.00** (`status=DONE`)
  - `random` (P1) Reward: **$0.00** (`status=DONE`)
  - Execution Time: 2.96 seconds
  - Crashes / Timeouts: 0 / 0

- **Deterministic Validation vs V023-G (Seed 42):**
  - Candidate (`v025_a`) vs `V023-G`: P0 = $26,855.00 vs P1 = $29,968.00
  - Promoted (`main.py`) vs `V023-G`: P0 = $26,855.00 vs P1 = $29,968.00
  - **Result: Exact deterministic match (0.00 discrepancy).**

---

## 3. Post-Promotion Regression-Test Results

### A. Fixed Seed Suite (`main.py` vs Random)
| Episode Seed | `main.py` Reward | Random Reward | Runtime | Status |
| :---: | :---: | :---: | :---: | :---: |
| **Seed 42** | $88,183.00 | $0.00 | 2.99s | DONE |
| **Seed 100** | $87,786.00 | $0.00 | 3.03s | DONE |
| **Seed 200** | $95,006.00 | $0.00 | 3.00s | DONE |
| **Seed 500** | $116,370.00 | $0.00 | 3.03s | DONE |
| **Seed 1000** | $98,554.00 | $0.00 | 3.05s | DONE |

### B. Fresh Paired H2H Suite (`main.py` vs `V023-G`)
- **Total Games:** 40 games (20 fresh paired seeds `9000..9019`)
- **Record:** 29 Wins / 11 Losses / 0 Ties
- **Win Rate:** **72.50%** (Aligns with full 2,000-game study benchmark of 72.25%)
- **`main.py` Mean Reward:** **$63,556.72**
- **`V023-G` Mean Reward:** **$58,787.50**
- **Paired Delta:** **+$4,769.22**

---

## 4. Git Status & Repository Hygiene

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   main.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	V025_PROMOTION_GATE.md
	V025_PROMOTION_RECORD.md
	agents/v025_f_adaptive_flywheel.py
	main_pre_v025a_promotion.py
	scripts/audit_v025_losses.py
	scripts/compare_v025_telemetry.py
	scripts/detailed_replay_divergence.py
	scripts/evaluate_v025_f_large_tournament.py
	scripts/execute_audit_suite.py
	scripts/fast_clean_runner.py
	scripts/fast_frontier_and_tournament.py
	scripts/inspect_loss_mechanisms.py
	scripts/run_efficient_frontier_sweep.py
	scripts/run_production_gate_benchmarks.py
	scripts/run_promotion_regression.py
	scripts/run_sequential_audit.py
	scripts/sweep_cow_strawberry_limits.py
	scripts/test_executor.py
	scripts/test_mp.py
	scripts/validate_v021_b_industrial.py
	scripts/verify_promotion.py
```

- `main.py` is the only modified tracked file.
- All controls, research scripts, and audit records are strictly intact.

---

## 5. Explicit Kaggle Submission Guard

- **Submission Executed:** **NO**
- **Kaggle CLI Invoked:** **NO**
- **Submission File Created:** **NO**
- **Readiness:** `main.py` is verified, byte-identical to `V025-A`, and standing by for explicit human approval prior to submission.
