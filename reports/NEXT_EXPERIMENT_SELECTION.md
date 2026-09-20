# Next Experiment Selection

## The Goal
To bridge the 3000+ rating gap without confounding variables, we must separate *structural farming route improvements* from *runtime market logic improvements*.

## Available Hypotheses based on 3000+ X-Ray

### Hypothesis 1: The Demand-Aware Logic Lift
Can we improve V057's performance purely by fixing its market logic, while keeping the same HIRE5 farming trace?
- **Observation**: Kaito v27 (3090.1) relies entirely on a Demand-Aware Market Ranking (`_order_score`, `_demand_per_day`) to avoid saturated markets. It explicitly does **not** use the blind `_front_run` lookahead that V057 uses.
- **Action**: Create EXP-038. Take V057, delete the `_front_run` logic, and port in the Kaito/Barnyard demand-aware market ranking. Run EXP-038 vs V057 to measure the pure logic lift.

### Hypothesis 2: The HIRE4 Route Supremacy
Is V057's HIRE5 trace fundamentally less efficient in raw agricultural output than Kaito's HIRE4 trace?
- **Observation**: Kaito diverges at Turn 1 by hiring only 4 hands instead of 5, which saves capital and creates a different game state tree. 
- **Action**: We would need to run an automated search (similar to Phase 3/4) constrained to HIRE4 to synthesize a new base trace, then compare its raw output to the HIRE5 trace.

### Hypothesis 3: The Barnyard Clone-Assassin
Does Barnyard's preemption logic work universally?
- **Observation**: No. Barnyard explicitly gates its preemption behind `_clone_distance <= 6`. It is a specialized weapon designed exclusively to win mirror matches against other trace-replay bots that are playing the same meta.
- **Action**: We should ignore this until our base trace and market logic are strong enough to actually encounter mirror matches at the top of the leaderboard.

## Recommendation
**Select Hypothesis 1.** 
We should immediately create EXP-038 to test the Demand-Aware Market Ranking. This is the lowest-hanging fruit and tests the most glaring difference in runtime logic between V057 and the 3000+ artifacts.

If EXP-038 proves successful, it becomes the new logic wrapper, and we can then move to Hypothesis 2 to search for a better base trace.
