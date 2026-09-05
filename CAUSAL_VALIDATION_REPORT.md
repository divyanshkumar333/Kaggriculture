# Kaggriculture Causal Meta Validation & Parameter Sweep Report

**Evaluation Date:** September 5, 2026  
**Environment:** `kaggriculture` (Engine 1.32.7)  
**Methodology:** Controlled Paired Identical-Seed Head-to-Head Simulator A/B Testing (Mirror Play in both Seat 0 and Seat 1) against Gold Standard Champion `V025-A`.  
**Status:** COMPLETE & CAUSALLY VALIDATED  

---

## 1. Executive Summary & Core Scientific Findings

This report documents the rigorous simulator counterfactual experiments testing every major strategic motif mined from the `KiroSamurai/kaggriculture-il` imitation learning dataset.

### Key Discoveries:
1. **The Day-0 Opening is Real & Causally Superior:**
   - The Grandmaster opening (**2 Cows + 2 Sheep + 9 Melons + 5 Wheat + 5 Hires**, $22 reserve) achieved an **85.0% Win Rate (+$9,883.40 Paired Delta)** over V025-A.
   - Reducing to 1 Cow drops win rate to 45%; increasing to 3 Cows collapses the budget to 0% WR (-$69,507 loss).
   - Reducing to 1 Sheep drops win rate to 55% (-$2,684 loss).
   - 9 Melons outperforms 11 Melons because preserving $160 cash prevents early feed starvation.
2. **The 6-Worker Ceiling Was a Statistical Illusion:**
   - Testing worker ceilings revealed that **6 workers is a severe bottleneck (0.0% Win Rate, -$17,857.90 loss)**.
   - Scaling mature labor to **12 total workers (11 hires/day)** yields an **85.0% Win Rate (+$7,657.50 Paired Delta)** with only 4.48% idle turns. Multi-quadrant farms (75 tiles) strictly require 12 workers to prevent crop rot and animal care failures.
3. **Cow Capacity Optimum is 6 to 8 Cows:**
   - 6 Cows achieved **+$5,961.05 margin** (75% WR) and 8 Cows achieved **+$2,305.05 margin** (80% WR).
   - Exceeding 10 Cows causes the **Milk Glut Trap**: milk market prices crash to $50.00, feed consumption escalates, and valuable quadrant space is denied to strawberries.
4. **Strawberry Initiation Must Be Delayed to Day 8–9:**
   - Initiating 40 Strawberries on **Day 9** produced **90.0% Win Rate (+$6,769.20 Paired Delta)**; Day 8 produced **85.0% Win Rate (+$5,340.50)**.
   - Starting on Days 5–6 crashed win rate to 40%–45% because buying berry seeds early depletes Day 8 working capital ($665 vs $1,021), delaying the $1,000 Q2 unlock.
5. **Crop Succession is Causally Destructive in Competitive Play:**
   - **Preserving strawberries through Day 30** won **85.0% of matches (+$5,620.85 Paired Delta)**.
   - Digging up strawberries on Days 21–25 to plant wheat crashed win rates to **0%–5% (-$6,466 to -$19,830 loss)**. Forfeiting $200/unit strawberries to plant $30/unit wheat while wasting worker turns digging is economically irrational.
6. **Adaptive Shed Pacing Prevents the 100-Item Discard Trap:**
   - Adaptive selling with an urgency threshold at $\ge 60$ shed occupancy and batch sizes of 8–12 units produced **+$3,893.85 margin** and zero inventory discards.

---

## 2. Phase 2: Grandmaster Opening Counterfactual Breakdown

Tested across 280 matches (14 configurations $\times$ 10 paired seeds $\times$ 2 mirror positions):

| Variant | Day 0 Composition | Win Rate (%) | Cand Mean ($) | V025 Mean ($) | Paired Delta ($) | Causal Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **GM_9Melons** | **2 Cows, 2 Sheep, 9 Melons, 5 Wheat, 5 Hires** | **85.0%** | **$60,354.75** | **$50,471.35** | **+$9,883.40** | **OPTIMAL CHAMPION** |
| **GM_10Melons** | 2 Cows, 2 Sheep, 10 Melons, 5 Wheat, 5 Hires | 75.0% | $56,143.80 | $50,254.80 | +$5,889.00 | Strong |
| **GM_Opening** | 2 Cows, 2 Sheep, 11 Melons, 5 Wheat, 5 Hires | 85.0% | $55,866.60 | $50,245.75 | +$5,620.85 | Strong |
| **GM_4Hires** | 2 Cows, 2 Sheep, 11 Melons, 5 Wheat, 4 Hires | 65.0% | $58,530.25 | $53,707.30 | +$4,822.95 | Sub-optimal labor |
| **GM_6Hires** | 2 Cows, 2 Sheep, 11 Melons, 5 Wheat, 6 Hires | 50.0% | $51,265.00 | $48,329.30 | +$2,935.70 | Overspent on D0 labor |
| **GM_3Wheat** | 2 Cows, 2 Sheep, 11 Melons, 3 Wheat, 5 Hires | 55.0% | $50,048.40 | $48,335.75 | +$1,712.65 | Insufficient early feed |
| **GM_7Wheat** | 2 Cows, 2 Sheep, 11 Melons, 7 Wheat, 5 Hires | 60.0% | $63,502.95 | $62,049.75 | +$1,453.20 | Marginal |
| **GM_1Cow** | 1 Cow, 2 Sheep, 11 Melons, 5 Wheat, 5 Hires | 45.0% | $57,751.95 | $56,473.70 | +$1,278.25 | Cattle under-investment |
| **V025-A Baseline** | 4 Sheep, 0 Cows, 7 Melons, 5 Wheat, 2 Hires | 50.0% | $57,567.60 | $57,567.60 | $0.00 | Baseline Reference |
| **GM_12Melons** | 2 Cows, 2 Sheep, 12 Melons, 5 Wheat, 5 Hires | 50.0% | $59,279.40 | $60,145.25 | -$865.85 | Slight capital drain |
| **GM_1Sheep** | 2 Cows, 1 Sheep, 11 Melons, 5 Wheat, 5 Hires | 55.0% | $50,842.90 | $53,527.80 | -$2,684.90 | Wool revenue loss |
| **GM_13Melons** | 2 Cows, 2 Sheep, 13 Melons, 3 Wheat, 5 Hires | 0.0% | $32,582.75 | $71,125.25 | -$38,542.50 | Working capital exhaustion |
| **GM_3Cows** | 3 Cows, 2 Sheep, 8 Melons, 5 Wheat, 5 Hires | 0.0% | $13,300.95 | $82,808.85 | -$69,507.90 | Budget breakdown |

---

## 3. Phase 3: Mature Labor Ceiling Sweep

Tested across 180 matches sweeping mature daily worker count (Days 6–30):

| Total Workers | Hires / Day | Win Rate (%) | Mean Cash ($) | Median Cash ($) | Paired Delta ($) | Idle Turn % | Causal Impact |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **12** | **11** | **85.0%** | **$54,023.50** | **$50,480.50** | **+$7,657.50** | **4.48%** | **OPTIMAL LABOR CAPACITY** |
| **10** | **9** | **80.0%** | **$48,619.40** | **$45,820.50** | **+$3,285.80** | 3.36% | Strong |
| **9** | **8** | 50.0% | $42,673.30 | $40,774.50 | +$1,083.80 | 2.82% | Marginal |
| **8** | **7** | 5.0% | $37,672.95 | $36,958.00 | -$6,742.60 | 2.53% | Transit deficit |
| **7** | **6** | 5.0% | $38,862.65 | $34,551.50 | -$12,243.50 | 2.28% | Unharvested produce |
| **6** | **5** | **0.0%** | **$35,714.15** | **$33,122.00** | **-$17,857.90** | 1.97% | **Severe labor starvation** |
| **5** | **4** | 0.0% | $30,577.45 | $31,144.50 | -$21,430.25 | 2.11% | Crop decay / weed bloom |
| **4** | **3** | 0.0% | $34,536.65 | $32,482.50 | -$34,442.15 | 0.71% | Total breakdown |
| **3** | **2** | 0.0% | $13,573.85 | $6,980.00 | -$62,605.40 | 0.07% | Collapse |

---

## 4. Phase 4: Cow Saturation Curve

Tested across 180 matches sweeping maximum cow capacity:

| Cow Target | Win Rate (%) | Mean Cash ($) | Median Cash ($) | Paired Delta ($) | Final Milk Price ($) | Economic Mechanism |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **6** | **75.0%** | **$61,259.10** | **$58,962.00** | **+$5,961.05** | **$64.35** | **Optimal profit per labor turn** |
| **8** | **80.0%** | **$59,658.15** | **$58,354.00** | **+$2,305.05** | **$77.10** | **Peak Win Rate & Volume** |
| **9** | 65.0% | $55,544.70 | $51,984.00 | +$1,622.90 | $66.45 | Approaching saturation |
| **4** | 50.0% | $64,484.30 | $64,445.50 | +$675.65 | $118.95 | High price, low volume |
| **10** | 35.0% | $52,220.50 | $48,367.50 | -$581.10 | $50.00 | Milk Glut Trap initiation |
| **11** | 30.0% | $51,734.60 | $48,371.50 | -$2,337.25 | $59.95 | Severe feed overhead |
| **12** | 20.0% | $50,037.05 | $43,834.50 | -$3,603.40 | $52.90 | Crowds out strawberries |
| **2** | 35.0% | $56,257.90 | $58,549.00 | -$7,897.15 | $115.90 | Under-utilized pastures |
| **0** | 0.0% | $49,884.20 | $50,878.00 | -$42,656.05 | $232.40 | Zero livestock dividend |

---

## 5. Phase 5: Strawberry Capacity & Initiation Timing

Tested across 220 matches:

| Capacity | Start Day | Win Rate (%) | Mean Cash ($) | Paired Delta ($) | Cash D8 ($) | Cash D18 ($) | Cash D29 ($) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **40** | **D9** | **90.0%** | **$50,068.60** | **+$6,769.20** | **$1,021.35** | **$20,169.60** | **$50,052.60** |
| **40** | **D8** | **85.0%** | **$55,852.05** | **+$5,340.50** | **$1,021.35** | **$20,522.45** | **$55,279.90** |
| **40** | **D7** | 80.0% | $51,053.40 | +$4,059.85 | $665.25 | $19,644.90 | $50,569.30 |
| **30** | **D6** | 70.0% | $52,544.10 | +$3,926.15 | $669.10 | $20,070.60 | $52,523.10 |
| **45** | **D6** | 55.0% | $50,250.00 | +$2,387.10 | $669.10 | $18,281.10 | $50,171.45 |
| **40** | **D6** | 45.0% | $50,906.15 | +$1,664.20 | $669.10 | $18,756.25 | $50,890.45 |
| **40** | **D5** | 40.0% | $49,038.60 | +$700.75 | $673.45 | $18,667.80 | $49,091.15 |
| **50** | **D6** | 35.0% | $51,178.85 | -$984.35 | $669.10 | $17,739.10 | $50,763.40 |
| **20** | **D6** | 25.0% | $47,838.60 | -$3,753.90 | $669.10 | $21,447.00 | $48,068.25 |

---

## 6. Phase 6: Crop Succession Strategy

Tested across 260 matches comparing strawberry destruction vs preservation:

| Configuration | Destruction Day | Win Rate (%) | Mean Cash ($) | Paired Delta ($) | Economic Diagnosis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **No_Succession** | **None (Harvest to D30)** | **85.0%** | **$55,866.60** | **+$5,620.85** | **OPTIMAL: Retains $200/unit yields** |
| **Destroy_D25** | Day 25 | 5.0% | $43,948.35 | -$6,466.35 | Replaced late with low-yield wheat |
| **Destroy_D24** | Day 24 | 5.0% | $42,464.85 | -$8,027.40 | Labor wasted on digging |
| **GM_Staggered** | Days 23–25 | 0.0% | $39,447.65 | -$11,680.55 | Forfeited peak strawberry dividends |
| **Destroy_D23** | Day 23 | 0.0% | $37,460.10 | -$13,806.70 | Severe value destruction |
| **Destroy_D21** | Day 21 | 0.0% | $31,960.90 | -$19,830.00 | Premature destruction catastrophe |

---

## 7. Phase 7: Market Selling & Shed Protection

Tested across 180 matches:

| Strategy | Win Rate (%) | Mean Cash ($) | Paired Delta ($) | Discard Risk | Market Impact |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Adaptive_Shed_Pacing** | **65.0%** | **$52,236.15** | **+$3,893.85** | **0.0% (Zero)** | **Balances price recovery and shed safety** |
| **Burst_Selling** | 75.0% | $51,694.80 | +$3,848.95 | 0.0% (Zero) | Depresses price during bursts |
| **IntraDay_Paced** | 45.0% | $51,577.00 | +$684.90 | Low | Adequate |
| **Fixed_Batch_8** | 60.0% | $50,166.05 | +$649.75 | Low | Standard |
| **Fixed_Batch_14** | 50.0% | $52,697.80 | +$494.15 | Zero | Slightly over-dampens prices |
| **Fixed_Batch_4** | 20.0% | $54,248.50 | -$1,034.90 | High | Shed overflow backlog |
