# V005 Benchmark Reconciliation

## The Discrepancy
In the initial V004 benchmark, `v004_b_diversify` scored an overall mean of **$33,559.23**.
In the initial V005 benchmark, its clone `v005_a_control` scored only **$29,234.42**.

## Investigation
A unified benchmark was created (`run_unified.py`) that strictly standardized the test environment across 90 games (vs `random`, `starter`, `melon_maxxer` across 30 identical seeds).

The discrepancy was traced to **Opponent Selection**.
In the V005 benchmark, `v005_a_control` was tested against `v004_b_diversify` (a mirror match) rather than `melon_maxxer`. Because both agents pursued identical optimal strategies (e.g., aggressively scaling MELON and STRAWBERRY), they directly competed for the same market inventory. This shared inventory saturated twice as fast, crashing the marginal sale price for both agents and heavily depressing the overall mean score.

## True Champion Established
When tested in the standardized, isolated environment (vs `random`, `starter`, `melon_maxxer`), the results were:

- `V004-B` (Crop Diversification): **$33,465.82**
- `V005-D` (Crop + Animal Optimizer): **$29,514.97**

**Conclusion:** `V004-B` remains the true champion. While V005-D successfully implemented positive marginal-ROI logic for animals, the actual execution of those tasks caused a catastrophic breakdown in the `TaskAllocator`, dragging down overall farm efficiency.

This establishes V004-B as the `V006-A` control.
