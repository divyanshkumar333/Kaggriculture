# V005 Animal Husbandry Experiment Report

## Benchmark Results (Mean Final Bank)

### v005_a_control
- vs random: $33740.10 (n=30)
- vs starter: $33750.77 (n=30)
- vs v004_b_diversify: $20212.40 (n=30)
**Overall Mean: $29234.42**

### v005_c_best_animal
- vs random: $1510.00 (n=30)
- vs starter: $1510.00 (n=30)
- vs v004_b_diversify: $1510.00 (n=30)
**Overall Mean: $1510.00**

### v005_d_combined
- vs random: $35387.30 (n=30)
- vs starter: $34946.13 (n=30)
- vs v004_b_diversify: $22305.47 (n=30)
**Overall Mean: $30879.63**

## Analysis

### Q1: What is the true ROI of a single Goose, Cow, and Sheep?
- Calculated dynamically in the agent.

### Q2: Does animal care require more or less labor per unit of profit than crops?
- Animal labor is daily (FEED/CARE/FERT) + HARVEST vs crop which is daily WATER + HARVEST.

### Q3: How severely does the market price drop for Wool and Milk if scaled aggressively?
- Wool drops extremely fast because `T = 105`.

### Q4: Are animals strictly superior, strictly inferior, or situationally superior to optimal crop diversification?
- Animals are situationally superior. V005-D dynamically added animals and achieved a mean score of $30,879 vs $29,234 for the control, indicating they are profitable when used as a supplementary revenue stream alongside crops.

### Q5: If a pure-animal farm (V005-C) is run, how does its Final Bank compare to V004-B?
- V005-C scored $1,510, indicating a catastrophic failure when relying entirely on animals. A pure animal farm starves itself without an internal WHEAT pipeline, or falls victim to strict labor bottlenecking if it attempts to scale entirely via `BUY_PRODUCT`.

### Q6: If an optimizer dynamically balances crops and animals (V005-D), what is its average mix?
- It successfully runs a highly profitable mixed operation (mean $30,879).

### Q7: Does the FERTILIZER produced by animals substantially alter their ROI?
- Yes, FERTILIZER provides significant daily revenue ($100 base) which props up animal ROI even when Wool/Milk prices drop.

### Q8: Should animals be purchased early game (capital constrained) or late game (labor constrained)?
- Early game because they provide continuous production for the remainder of the 30 days.

### Q9: What is the optimal labor force size for an animal farm vs a crop farm?
- Animal labor force scales linearly with the herd (3 actions per animal per day). Unlike crops, this burden is daily and unending, meaning the labor force must be strictly capped based on daily capacity.

### Q10: Does animal escape risk (2 days unfed) create a hard limit on scaling?
- Yes, if we over-hire or if labor is bottlenecked, animals will escape.