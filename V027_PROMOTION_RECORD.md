# Candidate V027 Internal Promotion Record

**Promotion Date & Timestamp:** September 5, 2026, 17:27:20 UTC+05:30  
**Status:** INTERNAL PROMOTION COMPLETE  
**Kaggle Submission Status:** NONE (Zero submissions made. Awaiting explicit user approval.)  
**Official Statement:** **V027 is the locally validated champion and is ready for a controlled Kaggle submission.**  

---

## 1. Cryptographic Hashes & Checksums

| Role | File Path | SHA-256 Checksum | Verification Status |
| :--- | :--- | :--- | :--- |
| **New Promoted Active Agent** | `main.py` | `86a2fd0b44a441c8e80e64ccdd7c0cef6ce1d8075387aac1f6bf09d335e86b86` | **MATCH (Identical to V027)** |
| **Candidate Source** | `agents/v027_hierarchical_meta.py` | `86a2fd0b44a441c8e80e64ccdd7c0cef6ce1d8075387aac1f6bf09d335e86b86` | **FROZEN CANDIDATE** |
| **Pre-Promotion Backup** | `main_pre_v027_promotion.py` | `255c716f9595bc0ef9ef06e0be44bacde87732a67f6e27bef192f0f80a903ffa` | **MATCH (Exact V025-A Backup)** |
| **Frozen V025-A Baseline** | `agents/v025_a_aggressive_cows.py` | `255c716f9595bc0ef9ef06e0be44bacde87732a67f6e27bef192f0f80a903ffa` | **100% INTACT & UNTOUCHED** |

---

## 2. Step 7 Promotion Regression Results

Evaluated across seeds 42, 101, 202, and 404 in both seat orders (Seat 0 and Seat 1):

| Seed | Seat | main.py Cash ($) | V025-A Cash ($) | Net Margin ($) | Result | Telemetry Violations |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | P0 | $58,292 | $54,826 | +$3,466 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **42** | P1 | $33,833 | $18,714 | +$15,119 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **101** | P0 | $42,926 | $20,925 | +$22,001 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **101** | P1 | $44,733 | $30,482 | +$14,251 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **202** | P0 | $51,977 | $45,843 | +$6,134 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **202** | P1 | $73,358 | $70,761 | +$2,597 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **404** | P0 | $59,287 | $51,232 | +$8,055 | **WIN** | None (0 starve, 0 weed, 0 discard) |
| **404** | P1 | $62,533 | $59,768 | +$2,765 | **WIN** | None (0 starve, 0 weed, 0 discard) |

- **Smoke & Syntax Check:** 100% Clean pass.
- **Exceptions:** 0.
- **Illegal Actions:** 0.
- **Animal Starvations / Escapes:** 0.
- **Worker Overflow / Out-of-bounds:** 0.
- **Shed Discards:** 0.

---

## 3. Step 8 Post-Promotion Paired Regression Benchmark

Evaluated across **100 fresh paired seeds (200 matches)** with mirrored seat orders (Seeds 60000–60099):

| Metric | main.py (V027) | V025-A Baseline | Difference / Performance |
| :--- | :---: | :---: | :---: |
| **Win Rate** | **92.0%** (184 Wins) | 8.0% (16 Wins) | **+84.0% Win Delta** |
| **Mean Final Cash** | **$59,729.51** | $50,724.15 | **+$9,005.35** |
| **Median Final Cash** | **$57,472.00** | $48,196.00 | **+$9,276.00** |
| **Paired Mean Margin** | — | — | **+$9,005.35 (+/- $6,632.01)** |
| **10th Percentile Margin (P10)** | — | — | **+$1,134.70 (Positive in 90%+ of games)** |
| **90th Percentile Margin (P90)** | — | — | **+$17,765.80** |
| **Candidate Reproducibility** | — | — | **100.0% Exact Match (0 discrepancies vs v027)** |

---

## 4. Governance & Kaggle Boundary Verification

- [x] `main_pre_v027_promotion.py` created as exact backup of old `main.py`.
- [x] `agents/v025_a_aggressive_cows.py` remains 100% intact with identical SHA-256 (`255c716f9595bc0ef9ef06e0be44bacde87732a67f6e27bef192f0f80a903ffa`).
- [x] `main.py` is byte-for-byte identical to `agents/v027_hierarchical_meta.py` (`86a2fd0b44a441c8e80e64ccdd7c0cef6ce1d8075387aac1f6bf09d335e86b86`).
- [x] Zero strategy alterations occurred during promotion.
- [x] Zero Kaggle submissions were made (no Kaggle API or CLI submission invoked).
- [x] Execution halted per instructions awaiting explicit user approval.
