# V006 Logistical Optimization Experiment Report

## Benchmark Results (Mean Final Bank)

### v006_a_control
- vs random: $34010.13 (n=30)
- vs starter: $33750.77 (n=30)
- vs melon_maxxer: $33230.93 (n=30)
**Overall Mean: $33663.94**

### v006_b_sectors
- vs random: $34105.53 (n=30)
- vs starter: $33750.77 (n=30)
- vs melon_maxxer: $33230.93 (n=30)
**Overall Mean: $33695.74**

### v006_c_tsp
- vs random: $29737.20 (n=30)
- vs starter: $30038.07 (n=30)
- vs melon_maxxer: $29776.03 (n=30)
**Overall Mean: $29850.43**

## Analysis

### Q1: Does V006-B (Sector Constraints) improve movement efficiency?
- No. Movement Efficiency remained at exactly 47.7%, identical to the control.

### Q2: Does V006-B (Sector Constraints) leave tasks uncompleted if a sector gets overloaded?
- No, it completed the same amount of tasks. Because the Hungarian algorithm is bipartite, if only 1 worker exists (e.g. the farmer), they will still be forced to take tasks in penalized sectors if no other worker is available, rendering the cost penalty irrelevant. The agent simply pays the cost and does the task anyway.

### Q3: Does V006-C (TSP / Non-Linear Distance) successfully cluster worker tasks?
- It penalized long walks too heavily, causing the agent to ignore high-priority dying plants across the farm. Movement efficiency actually dropped to 45.8% and Crop Deaths spiked from 12.1 to 13.9, devastating profitability.

### Q4: Which variant achieves the highest Mean Final Bank, and does it exceed V004-B ($33,465)?
- V006-B achieved $33,695.74 vs the control's $33,663.94, which is statistically indistinguishable from noise (a +0.09% variance). The structural logistical bottleneck (Movement Efficiency) remains unsolved.