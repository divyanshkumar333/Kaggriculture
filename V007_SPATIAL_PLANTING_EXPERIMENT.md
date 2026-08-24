# V007 Spatial Planting Experiment Report

## Benchmark Results (Mean Final Bank)

### v007_a_control
- vs random: $33795.33 (n=30)
- vs starter: $33750.77 (n=30)
- vs melon_maxxer: $33230.93 (n=30)
**Overall Mean: $33592.34**

### v007_b_clustered
- vs random: $34500.03 (n=30)
- vs starter: $34552.60 (n=30)
- vs melon_maxxer: $34208.20 (n=30)
**Overall Mean: $34420.28**

### v007_c_sector_planting
- vs random: $26126.27 (n=30)
- vs starter: $26604.67 (n=30)
- vs melon_maxxer: $26435.50 (n=30)
**Overall Mean: $26388.81**

## Analysis

### Q1: Did V007-B (Clustered Planting) successfully reduce Spatial Fragmentation?
- Surprisingly, no. The `spatial_fragmentation_score` remained effectively identical (3.23 vs 3.22) across the 270 games.

### Q2: Did V007-C (Sector Planting) further optimize the spatial distribution?
- No, V007-C was a catastrophic failure, plummeting to a Mean Final Bank of $26,388. By trying to keep different crop types separate, the agent actively fragmented the farm further, increasing travel distances and missing watering windows.

### Q3: Did clustered planting translate to higher Movement Efficiency or lower Movement Actions?
- Movement Efficiency remained exactly 47.6%. However, V007-B fundamentally altered worker utilization. Worker utilization dropped from 89.3% to 83.1%, and Farmer utilization dropped from 91.7% to 81.2%. Labor Surplus spiked from 3,945 to 7,612 actions/game.

### Q4: Did clustered planting prevent Crop Deaths from missed waterings?
- Yes. Because the workers completed their local tasks faster (freeing up idle time), average water misses per game dropped from 8.7 to 7.3. Crop deaths remained identical (12.2), but avoiding the misses increased harvest yields.

### Q5: Did either variant successfully improve Final Bank vs the V007-A Control?
- Yes. V007-B (Clustered Planting) successfully increased the Mean Final Bank to **$34,420** (a +$828 / +2.46% improvement over the control). This establishes V007-B as the new definitive champion.