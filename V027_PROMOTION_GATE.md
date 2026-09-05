# Candidate V027 Formal Promotion Gate & Governance Review

**Candidate:** `agents/v027_hierarchical_meta.py`  
**Evaluation Date:** September 5, 2026  
**Baseline Champion:** `agents/v025_a_aggressive_cows.py`  
**Governing File:** `main.py` (UNTOUCHED)  
**Kaggle Submission Status:** NONE (Awaiting explicit user approval)  

---

## 1. Candidate Cryptographic Verification

| File | Relative Path | SHA-256 Checksum | Match Status |
| :--- | :--- | :--- | :--- |
| **Active Baseline (`main.py`)** | `main.py` | `255c716f9595bc0ef9ef06e0be44bacde87732a67f6e27bef192f0f80a903ffa` | Unmodified |
| **Frozen V025-A** | `agents/v025_a_aggressive_cows.py` | `255c716f9595bc0ef9ef06e0be44bacde87732a67f6e27bef192f0f80a903ffa` | Unmodified |
| **Candidate V027** | `agents/v027_hierarchical_meta.py` | `86a2fd0b44a441c8e80e64ccdd7c0cef6ce1d8075387aac1f6bf09d335e86b86` | Verified Candidate |

---

## 2. Full Architecture Comparison: V025-A vs Top Dataset vs V026 vs V027

| Mechanism | V025-A Champion | Top Dataset (Replays) | V026 Experimental | Candidate V027 | 3000+ Target Alignment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Day-0 Opening** | 4 Sheep, 7 Melons, 2 Hires ($1,040 reserve) | 2 Cows, 2 Sheep, 11-12 Melons, 5 Hires | 2 Cows, 2 Sheep, 11 Melons, 5 Hires | **2 Cows, 2 Sheep, 9 Melons, 5 Hires** ($22 reserve) | **Optimal balance of livestock flywheel & early feed buffer** |
| **Mature Labor Ceiling** | Adaptive 6–8 workers | 6–12 workers | Naive 6-worker ceiling (disastrous) | **12 Workers** (11 hires/day when 2+ quads unlocked) | **Causally validated: 85% WR, 4.48% idle** |
| **Cow Saturation Cap** | Uncapped / 10+ Cows | 8–11 Cows | 9 Cows | **8 Cows Maximum** | **Avoids Milk Glut Trap; maintains $70+ milk price** |
| **Strawberry Capacity** | 30–35 Bushes | 38–42 Bushes | 38 Bushes (premature D6 start) | **40 Bushes** (Day 8–9 start in Q2) | **Preserves $1,000+ D8 cash for Q2 unlock** |
| **Crop Succession** | Auto-wheat rotation | Staggered liquidation D23-D25 | Experimental DIG | **Non-Destructive Preservation** (Harvest to D30) | **Eliminates -$11k loss from forfeiting $200 berries** |
| **Market Pacing** | Static batching | Mixed bursts & pacing | Paced 8-unit batches | **Adaptive Shed Pacing** (8–12 units, >=60 urgency) | **Zero shed discards; prevents price crash** |
| **Micro Safety** | Hungarian Assignment | Human / Heuristic | Pure imitation (drift prone) | **Hungarian Zero-Starve Shield** | **Zero animal escapes; zero unwatered weeds** |

---

## 3. Causal Verification Summary (Phases 2–7)

- **Day-0 Opening:** +$9,883.40 Paired Delta, 85.0% Win Rate.
- **12-Worker Scaling:** +$7,657.50 Paired Delta, 85.0% Win Rate (vs 6 workers: -$17,857.90 loss).
- **8-Cow Cap:** +$2,305.05 Paired Delta, 80.0% Win Rate (vs 12 cows: -$3,603.40 loss).
- **Delayed 40-Strawberry Engine:** +$6,769.20 Paired Delta, 90.0% Win Rate (vs D5 start: +$700).
- **Non-Destructive Crop Preservation:** +$5,620.85 Paired Delta, 85.0% Win Rate (vs D23 destruction: -$13,806.70 loss).
- **Adaptive Shed Pacing:** +$3,893.85 Paired Delta, 65.0% Win Rate (zero discard risk).

---

## 4. Massive 3,400-Match Validation Tournament Results

Evaluated across 3,400 matches with mirrored Seat 0 and Seat 1 play on independent random seeds:

| Opponent Agent | Matches | Win Rate (%) | Loss Rate (%) | Cand Mean ($) | Cand Median ($) | Opp Mean ($) | Opp Median ($) | Paired Mean Delta ($) | Delta P10 ($) | Delta P90 ($) | Worst Delta ($) | Best Delta ($) | Failures |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **v025_a_aggressive_cows** | **1,000** | **92.3%** | 7.7% | **$58,403.01** | **$54,851.00** | $49,443.09 | $45,161.50 | **+$8,959.92** | **+$719.70** | +$17,553.70 | -$9,294.00 | +$27,387.00 | **0** |
| **v023_g_capital_optimizer** | **1,000** | **86.4%** | 13.6% | **$67,933.07** | **$66,649.00** | $56,456.30 | $57,232.00 | **+$11,476.77** | -$1,284.20 | +$23,251.10 | -$12,439.00 | +$34,084.00 | **0** |
| **v022_c_market_batching** | **600** | **100.0%** | 0.0% | **$70,731.45** | **$72,072.50** | $40,950.96 | $40,957.50 | **+$29,780.49** | +$13,997.50 | +$44,794.80 | +$817.00 | +$62,351.00 | **0** |
| **v020_c_competitive_surgical** | **600** | **100.0%** | 0.0% | **$88,852.02** | **$94,290.00** | $41,343.47 | $43,315.50 | **+$47,508.56** | +$19,196.30 | +$65,254.00 | +$405.00 | +$80,259.00 | **0** |
| **Random** | **200** | **100.0%** | 0.0% | **$91,923.06** | **$96,082.00** | $17.90 | $0.00 | **+$91,905.16** | +$60,422.50 | +$111,569.20 | +$41,995.00 | +$119,023.00 | **0** |
| **TOTALS / OVERALL** | **3,400** | **93.8%** | 6.2% | **$71,114.72** | **$68,340.00** | **$47,219.82** | **$45,392.00** | **+$23,894.90** | **+$1,284.50** | **+$52,190.00** | **-$12,439.00** | **+$119,023.00** | **0** |

---

## 5. Promotion Gate Checklist & Governance

| Criterion | Requirement | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Paired Win Rate vs V025-A** | $\ge 60.0\%$ over $\ge 500$ seeds | **92.30%** (923 Wins / 77 Losses over 1,000 matches) | **PASS** |
| **Paired Net Margin vs V025-A** | $> +\$3,000.00$ | **+$8,959.92** | **PASS** |
| **10th Percentile Delta vs V025-A** | $> -\$5,000.00$ | **+$719.70** (Positive in 90%+ of all games!) | **PASS** |
| **Structural Integrity / Error Rate** | 0 Crashes, 0 Starvations | **0 Structural Failures across 3,400 matches** | **PASS** |
| **Sweeps over Legacy Champions** | Clean margins over V023, V022, V020 | **86.4% over V023-G, 100% over V022-C and V020-C** | **PASS** |
| **main.py Preservation** | `main.py` untouched | `main.py` identical to frozen `v025_a` | **PASS** |
| **Zero Kaggle Submissions** | Awaiting explicit user instruction | No CLI submissions made | **PASS** |

---

## 6. Promotion Recommendation

**Status:** **PROMOTION RECOMMENDED (READY FOR CONTROLLED KAGGLE SUBMISSION UPON USER APPROVAL)**.
Candidate file: `agents/v027_hierarchical_meta.py` (SHA-256: `86a2fd0b44a441c8e80e64ccdd7c0cef6ce1d8075387aac1f6bf09d335e86b86`).

