# Kaggriculture Champion & Control Ledger

## Current Champion
- **Candidate:** `agents/v036_v16_lookahead8.py`
- **Promoted:** 2026-09-11
- **SHA-256:** `646d9875df25ae4ca412610764d1364134f21f41a0c38b42c64802cc8894cbd3`
- **Benchmark Evidence vs V035_Champion:**
  - 100 paired fresh seeds (200 matches across both seats, seeds 5000-5099).
  - Match Win Rate: **99.0% (198W / 2L / 0T)**.
  - Paired Win Rate: **100.0% (100W / 0L / 0T)**.
  - Mean Paired Delta: **+$3,981**.
  - Mean Cash: $87,443 vs $85,453 (Net: +$1,990/match).
  - Robustness: 0 errors / 0 timeouts / 0 illegal actions.

## Current Runner-Up
- **Candidate:** `agents/v035_v16_lookahead7.py`
- **SHA-256:** `270c4a69b00dd087f663dea795560fde697a459e99717d0f7e0f56ea4b210fc1`
- **Description:** 7-step front-running lookahead with multi-step repayment schedule.

## Baselines & Controls

### V029 Impact-Ranked
- **File:** `agents/v029_v16_impact_ranked.py`
- **SHA-256:** `cacbca12f137354c2c9084fb6368fc3544dd2a843e7cbe3128aa14cd41337e44`
- **Description:** Clean price-impact sell-slot ordering on top of V16 foundation.

### V16-RC5 Baseline
- **File:** `agents/public_v16_rc5.py`
- **SHA-256:** `a710b168c5b6df72997323c61c795c870972fbf929e56bb1996fd8575ec84b83`
- **Description:** Reconstructed 8C/4S schedule + weed repair + 1-turn front-run + repay.

### V027 Control
- **File:** `agents/v027_hierarchical_meta.py`
- **SHA-256:** `2666960649f126c85792143a436d8a3e7609ecccb64f5de89f47806caee2cb04`
- **Description:** Hierarchical meta-policy with Hungarian safety shield.

### V025-A Control
- **File:** `agents/v025_a_aggressive_cows.py`
- **SHA-256:** `4eb096b363ff1ee0ffba6d2ed19a46f5653c09fc7142479a8a13297f3ae319b0`
- **Description:** Pre-V026 control with 4 sheep opening and aggressive cow ramp.

### Public V27 Meta Reset Reference
- **File:** `agents/public_v27_reset.py`
- **SHA-256:** `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
- **Description:** Kaito Fukami's 25->27 Strict Future V27 Midgame Meta Reset.

---

## Promotion History

| Version | Date | Promoted From | Reason / Benchmark Evidence | New SHA-256 |
|---|---|---|---|---|
| **V16-RC5** | 2026-09-11 | Foundation | 200W-0L vs V027, +$62,776 cash delta | `a710b168c5b6df72997323c61c795c870972fbf929e56bb1996fd8575ec84b83` |
| **V029_ImpactRanked** | 2026-09-11 | V16-RC5 | 189W-11L (94.5% win rate, 100/100 paired wins), +$1,783 paired delta | `cacbca12f137354c2c9084fb6368fc3544dd2a843e7cbe3128aa14cd41337e44` |
| **V030_Lookahead2** | 2026-09-11 | V029_Champion | 188W-12L (94.0% win rate, 100/100 paired wins), +$2,203 paired delta | `555bdc371fad0e3772c64dcd629ffbca6bbca31763ca244d53bd181a200102c8` |
| **V031_Lookahead3** | 2026-09-11 | V030_Champion | 198W-2L (99.0% win rate, 100/100 paired wins), +$3,574 paired delta | `3f9c8bce120506817908857c146dabe94b32162cdb01c2b0b092b2dd3b09fa4a` |
| **V032_Lookahead4** | 2026-09-11 | V031_Champion | 200W-0L (100.0% win rate, 100/100 paired wins), +$4,176 paired delta | `594d15145a8f3addff67c1e5bb125d345f7fbf7a3ea4992d0ff62049cb81ecae` |
| **V033_Lookahead5** | 2026-09-11 | V032_Champion | 196W-4L (98.0% win rate, 100/100 paired wins), +$3,334 paired delta | `2bb3533fe6969c0083b66acf4feb2de5c2c0aa911981682a9832ca20bd88d098` |
| **V034_Lookahead6** | 2026-09-11 | V033_Champion | 194W-6L (97.0% win rate, 100/100 paired wins), +$2,963 paired delta | `353623efdbcad81e56dff9c2d7d20408ec7317c3ac735e021ddc9ef7ad8bb484` |
| **V035_Lookahead7** | 2026-09-11 | V034_Champion | 195W-5L (97.5% win rate, 100/100 paired wins), +$3,694 paired delta | `270c4a69b00dd087f663dea795560fde697a459e99717d0f7e0f56ea4b210fc1` |
| **V036_Lookahead8** | 2026-09-11 | V035_Champion | 198W-2L (99.0% win rate, 100/100 paired wins), +$3,981 paired delta | `646d9875df25ae4ca412610764d1364134f21f41a0c38b42c64802cc8894cbd3` |
