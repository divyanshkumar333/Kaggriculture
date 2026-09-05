# Systematic Ablation Studies: V026 Architecture

**Evaluation Date:** September 5, 2026  
**Environment:** `kaggriculture` (Engine 1.32.7)  
**Methodology:** Controlled Paired Mirror Head-to-Head Testing against V025-A across identical seeds (6 seeds, 12 games per ablation).

---

## 1. Ablation Results Table

| Variant | Description | Mean Final Cash ($) | Cash Delta vs Full ($) | Head-to-Head Win Rate (%) | Margin vs V025-A ($) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Full_V026_A** | See below | `$48,596` | `+0` | `66.7%` | `+1,917` |
| **Ablation_No_D0_Cow** | See below | `$51,426` | `+2,829` | `33.3%` | `-1,321` |
| **Ablation_No_Cow_Velocity** | See below | `$56,496` | `+7,899` | `16.7%` | `-16,370` |
| **Ablation_No_Dynamic_Selling** | See below | `$46,692` | `-1,905` | `50.0%` | `-2,497` |

---

## 2. Component-by-Component Marginal Value

1. **Day 0 Cow Opening (+$-2,829 marginal cash):**
   Initiating with 1 Cow and 3 Sheep accelerates milk cashflow by Day 3. Removing it and reverting to 4 sheep delays liquidity generation by multiple days.

2. **Intra-Day Cow Velocity (+$-7,899 marginal cash):**
   Purchasing cows intra-day up to the 9-cow cap provides compound recurring income throughout the mid-game (Days 6-20).

3. **Dynamic Paced Selling (+$1,905 marginal cash):**
   Selling in small, price-sensitive batches prevents severe price depression and capitalizes on high market spikes.
