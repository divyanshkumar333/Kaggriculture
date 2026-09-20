# Contradictions Audit

This document records the major contradictions found between the various Markdown research reports, IL dataset analyses, and the actual executable code of the "champion" candidates.

## 1. Optimal Worker Ceiling (The Labor Paradox)

* **Claim A:** 12 Total Workers (11 Hires/day) is optimal, while 6 Workers yields a 0% win rate due to "severe labor starvation".
  * **Source:** `CAUSAL_VALIDATION_REPORT.md` (Phase 3)
  * **Date:** September 5, 2026
  * **Experiment:** 180 matches sweeping mature daily worker count (Days 6–30).
  * **Opponents:** `V025-A`
  * **Sample Size:** 180 matches
  * **Seeds / Seat handling:** 10 paired seeds x 2 mirror positions.
  * **Engine Version:** 1.32.7
  * **Metric:** Win Rate & Mean Cash

* **Claim B:** 6 Total Workers (5 Hires/day) is the strict "Saturation Ceiling" for 3000+ agents, saving over $8,000 compared to naive 12-15 worker agents.
  * **Source:** `KAGGRICULTURE_3000_PATH.md`
  * **Date:** September 5, 2026
  * **Experiment:** Mining the `KiroSamurai/kaggriculture-il` dataset & Top 1% Replays (Kawashigi tier).
  * **Sample Size:** 12,430 games
  * **Metric:** Kaggle Elo

* **Claim C:** Top 1% farms scale to 10.9 workers on Day 8 and 13.0 workers on Day 15.
  * **Source:** `IL_META_DISCOVERY.md`
  * **Date:** September 5, 2026
  * **Sample Size:** 886 High-Fidelity Player Trajectories
  
* **Code Evidence:** `026_the_golden_ratio.py` dynamically hires up to `num_quads * 3` hands (up to 12 hands/13 workers total), violating Claim B entirely despite being heralded as the 3000+ candidate.
* **Reproducible?** Local sweep required.
* **Current Confidence:** Low. The reports violently contradict each other on basic economic fundamentals.

## 2. Livestock Optimum (The Cow Capacity Trap)

* **Claim A:** 6-8 Cows is optimal. 10+ Cows causes the "Milk Glut Trap," crashing prices to $50 and destroying win rates.
  * **Source:** `CAUSAL_VALIDATION_REPORT.md` (Phase 4)
  * **Sample Size:** 180 matches

* **Claim B:** Top 1% farms (3000+ rating) reach 11.9 cows on Day 15 and 12.89 cows on Day 20.
  * **Source:** `IL_META_DISCOVERY.md`

* **Claim C:** The 9-Cow Cap is what prevents the milk glut collapse; 13 cows collapses win rate to 16.7%.
  * **Source:** `KAGGRICULTURE_3000_PATH.md` (Question 4)
  
* **Reproducible?** Sweep required.
* **Current Confidence:** Low.

## 3. Grandmaster Opening vs V026 Win Rate against V025-A

* **Claim A:** GM_9Melons (2 Cows, 2 Sheep, 9 Melons, 5 Wheat, 5 Hires) achieves an **85.0% Win Rate (+$9,883.40 Paired Delta)** over V025-A.
  * **Source:** `CAUSAL_VALIDATION_REPORT.md` (Phase 2)
  * **Sample Size:** 280 matches (14 configs x 10 paired seeds x 2 seats)

* **Claim B:** V026-A / V026-IL_META (which implements the GM opening) achieves a **66.7% head-to-head win rate and a +$1,917 net cash margin** over V025-A.
  * **Source:** `KAGGRICULTURE_3000_PATH.md`

* **Reproducible?** Requires local harness match.
* **Current Confidence:** Low. 85% WR and +$9.8k margin is completely inconsistent with 66.7% WR and +$1.9k margin for ostensibly the same strategy.

## 4. The 026 "Golden Ratio" Myth

* **Claim:** The 3000+ V026 strategy relies on dynamic cow expansion, a 6-worker pool, a 40-strawberry secondary engine, and a Hungarian safety shield.
* **Reality:** `026_the_golden_ratio.py` contains none of this. It hardcodes a spatial crop grid (`get_target_crop`), ignores cows and sheep completely, uses a greedy nearest-neighbor assignment instead of Hungarian matching, and hires 10+ hands.
* **Reproducible?** Code inspection proves the report describes an agent that does not exist in the 026 file.
* **Current Confidence:** The documentation regarding 026 is entirely fabricated or refers to a different file (possibly `v026_a_il_hybrid.py`, but even then, the claims are dubious).
