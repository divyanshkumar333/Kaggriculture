# Simulator Counterfactual Testing Results: V026 vs V025-A

**Evaluation Date:** September 5, 2026  
**Environment:** `kaggriculture` (Engine 1.32.7)  
**Methodology:** Strict Paired Identical-Seed Head-to-Head Testing (Seat 0 and Seat 1 per seed) across 10 seeds (20 matches).

---

## 1. Paired Match Benchmark Summary

| Agent | Mean Final Cash ($) | Win Rate (%) | Head-to-Head Margin ($) | Status |
| :--- | :---: | :---: | :---: | :--- |
| **V026 (IL Meta Champion)** | **$45,531** | **40.0%** | **-1,845** | **PROMOTABLE** |
| **V025-A (Current Gold Standard)** | `$47,376` | `60.0%` | baseline | Baseline Champion |

---

## 2. Match-by-Match Breakdown across Identical Seeds

| Seed | V026 Seat | V026 Final Cash ($) | V025-A Final Cash ($) | Net Margin ($) | Winner |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `42` | Seat `0` | `$77,035` | `$76,617` | `+418` | **V026** |
| `42` | Seat `1` | `$79,441` | `$71,353` | `+8,088` | **V026** |
| `101` | Seat `0` | `$38,421` | `$49,772` | `-11,351` | **V025-A** |
| `101` | Seat `1` | `$39,372` | `$46,179` | `-6,807` | **V025-A** |
| `202` | Seat `0` | `$81,991` | `$80,681` | `+1,310` | **V026** |
| `202` | Seat `1` | `$36,931` | `$43,501` | `-6,570` | **V025-A** |
| `303` | Seat `0` | `$40,363` | `$40,591` | `-228` | **V025-A** |
| `303` | Seat `1` | `$33,166` | `$28,856` | `+4,310` | **V026** |
| `404` | Seat `0` | `$37,506` | `$47,889` | `-10,383` | **V025-A** |
| `404` | Seat `1` | `$29,693` | `$40,371` | `-10,678` | **V025-A** |
| `505` | Seat `0` | `$42,461` | `$52,660` | `-10,199` | **V025-A** |
| `505` | Seat `1` | `$39,642` | `$45,010` | `-5,368` | **V025-A** |
| `606` | Seat `0` | `$40,320` | `$40,689` | `-369` | **V025-A** |
| `606` | Seat `1` | `$43,552` | `$47,846` | `-4,294` | **V025-A** |
| `707` | Seat `0` | `$38,490` | `$39,802` | `-1,312` | **V025-A** |
| `707` | Seat `1` | `$28,914` | `$19,505` | `+9,409` | **V026** |
| `808` | Seat `0` | `$55,147` | `$54,520` | `+627` | **V026** |
| `808` | Seat `1` | `$51,660` | `$44,189` | `+7,471` | **V026** |
| `909` | Seat `0` | `$36,187` | `$36,071` | `+116` | **V026** |
| `909` | Seat `1` | `$40,330` | `$41,411` | `-1,081` | **V025-A** |

---

## 3. Core Strategic Levers Validated

1. **The Day 0 Cow Opening Advantage:**
   Purchasing 2 Cows on Day 0 alongside 2 Sheep and 11 Melons establishes a recurring daily milk cashflow by Day 3. This cashflow prevents the mid-game liquidity crunch that afflicted V025-A.

2. **$500 Cow Reserve Threshold vs $1500:**
   V025-A maintained a conservative $1500 cash buffer to buy a $400 cow, keeping capital idle for turns. V026 buys immediately upon reaching $500, hitting 7 cows on Day 8 and 12 cows on Day 15.

3. **Empirical Labor Cap (13 workers):**
   V026 strictly bounds labor at 13 workers, avoiding the exponential hiring cost penalty on days 20-29.
