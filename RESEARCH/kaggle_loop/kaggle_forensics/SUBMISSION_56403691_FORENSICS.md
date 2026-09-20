# Forensic Investigation: The 310.6 / 449.8 Score Collapse (Submission 56403691)

## 1. Case Metadata
- **Submission ID**: `56403691`
- **Submission Date**: 2026-09-20 18:30:40 UTC
- **Package**: `submission.tar.gz` (V058 Generalized Spoiler Candidate)
- **Initial Rating**: 600.0 (default Kaggle Glicko2 prior)
- **Rating Trajectory**: Dropped from 600.0 -> 449.8 (and touched 310.6 provisional during early matchmaking)
- **Episode Count**: 5 public episodes (111321518, 111322613, 111323776, 111324880, 111326061)

## 2. Root Cause Determination
**Primary Classification**: `B` (Packaging/Script Corruption) leading to `F` (Disastrous Economic Execution).

### Detailed Mechanism:
1. Prior to submission 56403691, a utility script `scratch/fix_memory.py` was executed with the intention of reducing memory usage when packaging V057/V058.
2. `fix_memory.py` stripped the critical 5-hand (`HIRE5`) Day 0 opening trace and replaced it with a dynamic fallback to an unverified payload.
3. In actual match execution (e.g. Episode 111326061), Step 1 actions diverged fatally:
   - **Intended V057/V058 Behavior**: `[['BUY_PRODUCT', 'WHEAT', 14], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]` -> 5 workers hired on Day 0, bootstrapping 1 Cow, 4 Sheep, and 10 Wheat plants by Day 1.
   - **Corrupted 56403691 Behavior**: `[['HIRE'], ['BUY_SEED', 'MELON', 25]]` -> Only 1 worker hired on Day 0, spending all starting capital on 25 Melon seeds.
4. **Economic Consequence**:
   - With only 1 worker and 0 livestock, the farm could not water 25 melon plants. Plants decayed into weeds.
   - Zero wool, zero milk, zero recurring livestock revenue.
   - Final cash collapsed to **$19,106**, losing trivially to standard public bots ($46,143).

## 3. Ground-Truth Proof via Verification
- In Episode 111326061 (corrupted 56403691): P0 scored $19,106 vs P1 $46,143.
- In Episode 111325919 (repaired V057 Control 56403913): P0 scored **$129,374** vs P1 $68,225.
- In Episode 111327022 (repaired V058 Challenger 56403931): P1 scored **$125,456** vs P0 $43,776.
- In Episode 111328124 (repaired V058 Challenger 56403931): P0 scored **$152,412** vs P1 $102,578.

## 4. Current Recovery Status
- **56403913** (V057 Control): 3 wins, 0 losses, rating risen from 600.0 -> 855.6.
- **56403931** (V058 Challenger): 2 wins, 0 losses, rating risen from 600.0 -> 767.4.
- Both active submissions are climbing rapidly.
