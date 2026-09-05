# Current Kaggle Leaderboard Meta Research (Target 3000+)

**Document Version:** 1.0  
**Research Date:** September 5, 2026  
**Objective:** Reverse-engineer the current top-tier Kaggle leaderboard meta (2500–3064+ rating) and establish the concrete structural gap between V025-A and the #1–#3 Kaggle champions.

---

## 1. Current Leaderboard Top 20 Landscape

From live Kaggle Leaderboard mining:

| Rank | Team Name | Team ID | Live Rating | Submission Date | Meta Lineage |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **#1** | **keiz** | 16767215 | **3064.9** | 2026-09-03 | Dual Livestock + Melon Burst + Strawberry/Wheat Succession |
| **#2** | **Jesse Bullard** | 16621243 | **2988.5** | 2026-09-04 | Dual Livestock + Melon Burst + Multi-Quad Expansion |
| **#3** | **Andrey Tikhomirov** | 16749520 | **2930.9** | 2026-09-04 | Day 0 Livestock Engine + Early Strawberry Hybrid |
| **#4** | **MtN** | 16655383 | **2900.0** | 2026-09-04 | 3-Quadrant Agro-Industrial Multi-Product |
| **#5** | **Dmytro Maliarenko** | 16798172 | **2880.1** | 2026-09-04 | High-Velocity Livestock + Crop Rotation |
| **#6** | **Bohannn Wang** | 16730946 | **2876.6** | 2026-09-04 | Fast-Cow + Active Strawberry Succession |
| **#7** | **Giulio Ravasio** | 16674508 | **2861.6** | 2026-09-04 | Intensive Day 0 Livestock Opening |
| **#8** | **LagrangianLocomotive** | 16735252 | **2852.2** | 2026-09-04 | Spatial Hungarian Routing + Adaptive Liquidation |
| **#9** | **OceanMix** | 16662883 | **2843.3** | 2026-09-04 | Multi-Product Town Sink Optimizer |
| **#10** | **Atakan Aldemir** | 16711752 | **2835.6** | 2026-09-04 | Hybrid Cattle / Berry Dual Engine |
| **#11** | **Syed Asad Ali** | 16685634 | **2831.2** | 2026-09-04 | Fast Melon Jumpstart |
| **#12** | **薄和叶 Lv.INF** | 16743484 | **2829.6** | 2026-09-03 | Continuous Animal Feeding Engine |
| **#13** | **kwa** | 16739633 | **2823.7** | 2026-09-05 | Aggressive Land Q2/Q3 Expansion |
| **#14** | **YUK** | 16730735 | **2818.2** | 2026-09-04 | High-Yield Succession Loop |
| **#15** | **mandgeee** | 16654704 | **2804.1** | 2026-09-04 | Multi-Worker Task Scheduler |
| **#16** | **Sebastian Mateus** | 16654379 | **2800.0** | 2026-09-04 | Dual Livestock Opening |
| **#17** | **Yuan800** | 16698308 | **2799.4** | 2026-09-04 | Berry Lifecycle Harvesting |
| **#18** | **Thomas Deng** | 16786109 | **2798.1** | 2026-09-05 | Market Batching & Town Exploiter |
| **#19** | **MaxZhuCHN** | 16779254 | **2778.6** | 2026-09-04 | Industrial Strawberry Engine |
| **#20** | **l1aF** | 16715235 | **2772.9** | 2026-09-04 | Fast Cash-Cycle Opening |

---

## 2. Telemetry Comparison: V025-A vs Top Replays

Detailed checkpoint progression extracted directly from Kaggle public replay binaries:

### A. Top Kaggle Champion (`AI After Hours`, Ep 103388734 — $162,805)
| Day | Bank | Cows | Sheep | Strawberries | Wheat | Melons | Quads | Workers | Primary Phase Focus |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **D0** | $3,000 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | Day 0 Spend: 7 Melons + 9 Wheat |
| **D2** | $116 | 0 | 0 | 0 | 9 | 7 | 1 | 1 | Wheat harvest #1, first cash recovery |
| **D4** | $495 | 0 | 0 | 3 | 10 | 7 | 1 | 1 | First strawberries planted (Day 4!) |
| **D5** | $41 | 1 | 0 | 3 | 10 | 7 | 1 | 1 | First Cow bought (Day 5) |
| **D6** | $143 | 1 | 0 | 7 | 6 | 7 | 1 | 1 | Melons mature; 7 Strawberries active |
| **D7** | $1,599 | 2 | 0 | 12 | 5 | 7 | 2 | 1 | **Buys Q2 (NE)**; 12 Strawberries active |
| **D8** | $860 | 6 | 0 | 20 | 10 | 7 | 2 | 1 | Rapid cattle scale (6 Cows); 20 Strawberries |
| **D10** | $2,704 | 9 | 0 | 22 | 8 | 7 | 2 | 1 | 9 Cows producing; Melon round 2 matures |
| **D12** | $8,975 | 11 | 0 | 41 | 7 | 4 | 3 | 1 | **Buys Q3 (SW)**; 41 Strawberries active |
| **D15** | $16,570 | 11 | 0 | 41 | 12 | 4 | 3 | 1 | Peak dual engine: 11 Cows + 41 Strawberries |
| **D18** | $44,102 | 11 | 0 | 41 | 15 | 4 | 3 | 1 | Massive cash generation ($44K bank) |
| **D21** | $68,855 | 11 | 0 | 38 | 18 | 4 | 3 | 1 | **Succession begins**: Digs 3 berry bushes -> Wheat |
| **D24** | $105,892 | 11 | 0 | 28 | 29 | 0 | 3 | 1 | **Heavy succession**: 28 Berry / 29 Wheat |
| **D27** | $129,853 | 11 | 0 | 8 | 40 | 0 | 3 | 1 | **Final succession**: 8 Berry / 40 Wheat |
| **D29** | $146,911 | 11 | 0 | 0 | 30 | 0 | 3 | 1 | **Liquidation**: Sells all produce -> $162,805 |

---

### B. Current High-Rating Champion (`yjshyfy`, Ep 104882243 — $116,533)
| Day | Bank | Cows | Sheep | Strawberries | Wheat | Melons | Quads | Workers | Primary Phase Focus |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **D0** | $3,000 | 2 | 2 | 0 | 7 | 12 | 1 | 6 | **Instant Day 0 Dual Livestock (2 Cows + 2 Sheep) + 12 Melons** |
| **D2** | $141 | 3 | 2 | 0 | 7 | 12 | 1 | 5 | Buys 3rd Cow (Day 2!); Wheat feeds livestock |
| **D4** | $118 | 4 | 2 | 0 | 7 | 12 | 1 | 5 | Buys 4th Cow (Day 3-4!); Plants 4 Strawberries |
| **D6** | $239 | 6 | 2 | 4 | 3 | 12 | 2 | 9 | **Melon jackpot on Day 6; Buys Q2 + 2 Cows + 8 Berry** |
| **D8** | $408 | 8 | 4 | 16 | 9 | 12 | 2 | 11 | 8 Cows + 4 Sheep (12 livestock!) + 16 Berry |
| **D10** | $2,688 | 9 | 4 | 20 | 5 | 12 | 2 | 12 | Huge product sales; Prepares Q3 expansion |
| **D12** | $17,213 | 9 | 4 | 38 | 20 | 0 | 3 | 10 | **Buys Q3 (SW)**; 38 Strawberries active |
| **D15** | $27,771 | 9 | 4 | 38 | 23 | 0 | 3 | 13 | Steady multi-product daily sales |
| **D18** | $40,417 | 9 | 4 | 38 | 22 | 0 | 3 | 13 | 12-13 workers harvesting & tending |
| **D21** | $58,497 | 9 | 4 | 38 | 23 | 0 | 3 | 13 | Peak production, starts strawberry dig phase |
| **D24** | $81,492 | 9 | 4 | 26 | 35 | 0 | 3 | 13 | Replaces decaying berries with 35 fast Wheat |
| **D27** | $95,731 | 9 | 4 | 18 | 39 | 0 | 3 | 12 | Sells steady produce; wheat rapid harvesting |
| **D29** | $108,212 | 9 | 4 | 0 | 23 | 0 | 3 | 12 | Complete liquidation -> $116,533 |

---

### C. Promoted Candidate V025-A (Ep 105710071 — $83,998)
| Day | Bank | Cows | Sheep | Strawberries | Wheat | Melons | Quads | Workers | Deficiencies vs Top Meta |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **D0** | $3,000 | 0 | 0 | 0 | 2 | 6 | 1 | 1 | **Too weak opening**: only 6 Melons, 0 livestock |
| **D2** | $114 | 0 | 0 | 0 | 2 | 6 | 1 | 1 | Idle cash capacity, 0 early milk/wool |
| **D4** | $704 | 0 | 0 | 0 | 1 | 6 | 1 | 1 | 0 animals, 0 strawberries (4 days behind) |
| **D6** | $1,145 | 0 | 0 | 0 | 0 | 6 | 1 | 1 | Melons mature but no land bought until D7 |
| **D7** | $5,130 | 1 | 0 | 0 | 0 | 6 | 2 | 2 | Buys Q2 late; only 1 Cow |
| **D8** | $2,406 | 6 | 0 | 0 | 0 | 6 | 2 | 7 | Fast cow catchup, but 0 strawberries |
| **D10** | $1,654 | 10 | 0 | 2 | 0 | 6 | 2 | 11 | Reaches 10 cows, but berry engine just starting |
| **D12** | $5,186 | 11 | 0 | 31 | 0 | 0 | 3 | 12 | Reaches 31 berries (5 days later than #1) |
| **D15** | $9,857 | 11 | 0 | 35 | 0 | 0 | 3 | 12 | Bank is $10K vs $28K for top meta |
| **D18** | $27,967 | 11 | 0 | 35 | 0 | 0 | 3 | 12 | Healthy cash, but no wheat feed self-sufficiency |
| **D21** | $41,632 | 11 | 0 | 35 | 0 | 0 | 3 | 12 | **No succession**: retains 35 expiring berries |
| **D24** | $58,899 | 11 | 0 | 32 | 0 | 0 | 3 | 12 | Expiring berries produce 0 yield; 0 wheat planted |
| **D27** | $76,221 | 11 | 0 | 26 | 3 | 0 | 3 | 12 | Only 3 wheat planted; massive lost yield |
| **D29** | $84,637 | 11 | 0 | 5 | 6 | 0 | 3 | 12 | Delayed liquidation -> $83,998 |

---

## 3. The 3000-Tier Formula: Gap Analysis

| Strategic Dimension | V025-A Policy | 3000-Tier Champion Policy | Impact on Score |
| :--- | :--- | :--- | :--- |
| **Day 0 Opening** | 6 Melons, 2 Wheat, 0 Animals | **12 Melons, 7 Wheat, 2 Cows + 2 Sheep (or 15 Melons + 10 Wheat)** | **+$8,000–$15,000** early compound capital |
| **Day 0–5 Livestock** | Starts Day 7 | **Active Day 0 (2 Cows + 2 Sheep)** produces Milk/Wool/Fertilizer from Day 1 | **+$6,000** early product revenue |
| **Strawberry Start** | Day 10–12 | **Day 4–6** (Plants 4–8 bushes immediately as early cash clears) | **+$15,000–$25,000** extra berry harvest cycles |
| **Land Expansion** | Q2 on D7, Q3 on D12 | **Q2 on D6 (immediately upon Melon harvest), Q3 on D11** | Unlocks 50–75 tiles 2 days earlier |
| **Feed Management** | Buys wheat from market | **Grows self-sustaining 7–10 wheat buffer on farm** | Saves $10/unit seed vs high market product price |
| **Late-Game Succession** | Leaves berries until D28 | **Active Digs on D21–D26 -> 30–40 Wheat speed cycles** | **+$20,000–$35,000** late-season cash injection |
| **Final Liquidation** | Day 29–30 | **Day 28–29 complete field clearing + batch dump** | 0 wasted field inventory |

---

## 4. Policy Lineage Synthesis for Candidate V026

To reach the 3000+ rating tier, Candidate V026 must unite all 4 pillars of the verified top meta:

1. **Day 0 High-Yield Turbo Opening:**
   - 12 Melons + 7 Wheat + 2 Cows + 2 Sheep + 4 Pastures (or 15 Melons + 10 Wheat + 4 workers).
2. **Early Strawberry & Livestock Acceleration (Days 4–8):**
   - Day 4: Begin planting 4–8 Strawberry bushes.
   - Day 6: Melon harvest windfall -> Buy Q2 immediately -> Scale to 8 Cows + 4 Sheep + 20 Strawberries.
3. **Mid-Game Dual Production Powerhouse (Days 9–20):**
   - 12 Livestock (8–10 Cows, 2–4 Sheep) + 38 Strawberries + 15 Wheat in Q1/Q2/Q3.
   - 11–13 workers maintaining 100% daily watering, feeding, and caring.
4. **Active Late-Game Succession (Days 21–28):**
   - Day 21+: As strawberries pass yield cap, DIG 4–6 bushes daily and immediately plant Wheat/Carrots.
   - Harvests 2–3 full cycles of rapid wheat (2 days to harvest) before Day 30 liquidation.
