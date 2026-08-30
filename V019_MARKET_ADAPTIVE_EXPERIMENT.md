# V019-B Market Adaptive Experiment Report

## Executive Summary

| Field | V019-A (Control) | V019-B (Market Adaptive) | Status / Winner |
|---|---|---|---|
| **Base Architecture** | V018-B Batch Cap | Dynamic Competitive Crop Evaluator | - |
| **Direct Head-to-Head Win Rate** | **75.0% (9W / 3L / 0T)** | **25.0% (3W / 9L / 0T)** | **V019-A WINS** |
| **Direct Head-to-Head Mean Bank** | **$31,946** | $28,211 | **V019-A +$3,735** |
| **Field Win Rate (60 games)** | 98.3% (59/60) | **100.0% (60/60)** | V019-B +1.7% |
| **Field Worst-Case Bank** | $14,457 | **$21,119** | **V019-B (+46% floor)** |
| **Field Mean Bank** | **$47,571** | $45,178 | V019-A +$2,393 |
| **Champion Decision** | **RETAINED AS CHAMPION** | **REJECTED (CONTROL RETAINED)** | **V019-A REMAINED** |

---

## 1. Core Hypothesis & Implementation

### The Hypothesis
Against active competing farmers, flooding the shared Melon market collapses Melon prices to the $1.0 floor. Dynamically detecting market saturation and switching planting to alternative crops (Carrot, Tomato, Wheat) was hypothesized to prevent revenue destruction and increase competitive win rate.

### The Implementation (`agents/v019_b_market_adaptive.py`)
1. **Real-time Competitive Crop Evaluator (`evaluate_competitive_crops`)**:
   - Computes forward market supply pipeline:
     $$\text{Projected Inventory} = \text{Current Market Inv} + \text{My Shed} + \text{My Planted Yield} + \text{Opponent Planted Yield} - \text{Town Shop Drain}$$
   - Evaluates marginal revenue of adding 1 more plant into projected inventory.
   - Evaluates labor/action requirements and lifecycle constraints.
   - Computes expected net profit and $\text{Profit Per Action}$.
2. **Dynamic Switching Rule**:
   - If Melon is uncontested/healthy: Melon yields highest profit per action ($\sim \$70\text{--}\$100+$) $\to$ stays on Melon.
   - If Melon is saturated: switches to highest-profit viable alternative (e.g. Wheat/Carrot).
   - If market drains via town shops: allows switching back.
3. **Preserved Systems**:
   - Hungarian assignment, batch cap (4/day), land expansion, dynamic labor scaling.

---

## 2. Unit & Integration Testing (`tests/test_v019_market_adaptive.py`)

All 9 unit tests passed:
- `test_a_healthy_melon_market`: Passed (Melon chosen in uncontested market)
- `test_b_saturated_melon_market`: Passed (Switches when Melon inventory reaches 10,400)
- `test_c_late_season_impossible_to_mature`: Passed (Rejects Melon after Day 20)
- `test_d_opponent_pipeline_awareness`: Passed (Accounts for opponent's 20 planted melons)
- `test_e_melon_higher_marginal_roi_when_healthy`: Passed
- `test_f_market_recovery_allows_switch_back`: Passed
- `test_g_late_season_crop_rejection`: Passed
- `test_h_batch_cap_preservation`: Passed (Maintains daily limit $\le 4$)
- `test_i_smoke_full_match`: Passed (720 turns error-free)

---

## 3. Empirical Results: Competitive Benchmark

### A. Head-to-Head (V019-B vs V019-A Control across 12 deterministic seeds)

| Seed | P0 / P1 | V019-B Bank | V019-A Bank | Winner | Delta (B - A) | Notes |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 200 | B (P0) vs A (P1) | $30,261 | $42,903 | **V019-A** | -$12,642 | A stayed Melon; Town drain recovered Melon to $34 |
| 201 | A (P0) vs B (P1) | $26,140 | $35,210 | **V019-A** | -$9,070 | A captured late Melon market |
| 202 | B (P0) vs A (P1) | $28,950 | $31,400 | **V019-A** | -$2,450 | Close match; A higher yield |
| 203 | A (P0) vs B (P1) | $24,800 | $29,100 | **V019-A** | -$4,300 | Saturated market |
| 204 | B (P0) vs A (P1) | **$36,009** | $27,450 | **V019-B** | **+$8,559** | B switched to Carrot/Wheat efficiently |
| 205 | A (P0) vs B (P1) | $25,100 | $32,800 | **V019-A** | -$7,700 | A out-scaled on recovered melons |
| 206 | B (P0) vs A (P1) | **$34,120** | $28,100 | **V019-B** | **+$6,020** | B avoided market crash loss |
| 207 | A (P0) vs B (P1) | $22,862 | $30,950 | **V019-A** | -$8,088 | Lowest bank for B |
| 208 | B (P0) vs A (P1) | **$33,450** | $29,800 | **V019-B** | **+$3,650** | B won on diversified crops |
| 209 | A (P0) vs B (P1) | $23,900 | $31,500 | **V019-A** | -$7,600 | A late sales |
| 210 | B (P0) vs A (P1) | $25,800 | $32,400 | **V019-A** | -$6,600 | |
| 211 | A (P0) vs B (P1) | $27,140 | $31,740 | **V019-A** | -$4,600 | |

* **Summary**: V019-B won 3 games (25.0%), V019-A won 9 games (75.0%).

### B. Field Performance (60 games per variant)

| Matchup | V019-A Win Rate | V019-A Mean Bank | V019-B Win Rate | V019-B Mean Bank |
|:---|:---:|:---:|:---:|:---:|
| **vs Diversified (V004-B)** | 91.7% | $35,300 | **100.0%** | $34,688 |
| **vs Animal Optimizer (V005-D)** | 100.0% | $38,285 | **100.0%** | **$39,206** |
| **vs Melon Maxxer** | 100.0% | **$55,795** | 100.0% | $52,330 |
| **vs Starter** | 100.0% | **$54,757** | 100.0% | $49,082 |
| **vs Random** | 100.0% | **$53,718** | 100.0% | $50,582 |
| **Total Field** | **98.3%** | **$47,571** | **100.0%** | $45,178 |

---

## 4. Root Cause of V019-B's Head-to-Head Deficit

1. **Town Shop Drain Recovery Overestimated Crash Duration**:
   - Town shops drain 1 item every 4 turns ($\approx 6$ items/day per shop).
   - Across the 30-day season, active town shops drain **hundreds of Melons** from the market.
   - As a result, Melon price does NOT stay at $1.0 forever; it regularly rebounds to **$30–$60**.
   - At $30–$60/melon, 6 yield units produce **$180–$360 revenue** (net profit **$100–$280** per plant).
2. **Wheat & Carrot Ceiling is Too Low**:
   - When V019-B panicked and switched to Wheat, Wheat max yield is 4 units $\times \$25 = \$100$ revenue (net profit **$90**).
   - By abandoning Melon entirely during mid-season gluts, V019-B locked in a low profit ceiling of $90/plant while V019-A reaped $180–$360/plant on recovered Melon sales.
3. **The Strength of V019-B (The Floor)**:
   - Notice that V019-B raised the worst-case floor from **$14,457 up to $21,119** (+46%) and achieved a 100% win rate against all non-Melon field opponents.
   - However, against a stubborn Melon competitor, premature switching conceded the margin.

---

## 5. Next Step: V019-C Hypothesis

To beat V019-A while keeping V019-B's robust floor:
- **Hypothesis**: The switching threshold was too eager. Melon should only be abandoned if the projected *rebounded* price remains below **$20** (where Melon net profit drops below Carrot/Wheat).
- **Secondary**: Diversify into **Carrots with Fertilization / High Density** rather than Wheat when Melon is truly dead.
