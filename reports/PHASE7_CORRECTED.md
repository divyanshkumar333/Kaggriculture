# Phase 7 Correction Report

## The Error in Prior Analysis
The original Phase 7 analysis concluded that our local champion, V057, was competitive with 3000+ public artifacts up to the midgame (Turn 218 for Kaito, Turn 552 for Barnyard). It hypothesized that the gap to 3000+ was due to late-game meta-resets and blind front-running failures.

**This entire premise was flawed.**
The files used for the original analysis (`RESEARCH/opponents/kaito_v27.py` and `RESEARCH/opponents/barnyard_v7.py`) were not the actual public artifacts. They were synthetic approximations built by modifying our own V057 trace based on human descriptions. Consequently, the "midgame divergence" was artificially constructed.

## The Corrected Reality
By downloading and X-Raying the **real** Kaggle outputs (`kaitofukami/25-27-strict-future-v27-midgame-meta-reset` and `romanrozen/strong-barnyard-economist`), we discovered:

1. **Divergence at Turn 1**: The real artifacts are not derived from V057's HIRE5 Cow trace. Kaito uses a HIRE4 Cow trace. Barnyard uses a SHEEP trace. The tactical divergence happens on the very first move of the game.
2. **The Front-Running Fallacy**: Kaito v27 (3090.1) does not use *any* front-running or future-lookahead logic. It simply uses a standard trace and a dynamic market algorithm. This proves V057's brittle `_front_run` logic is over-engineered and unnecessary.
3. **The True Market Meta**: Both Kaito and Barnyard use the exact same **Demand-Aware Market Ranking** formula. Instead of just picking the item with the lowest raw price drop, they calculate `_demand_per_day` for the Town shops and apply an urgency modifier to items that are over-supplied. 
4. **Barnyard's Innovation**: Barnyard does use preemption, but only as an "Adaptive Clone-Assassin." It proves the opponent is playing a similar trace (`_clone_distance <= 6`), looks into its *own* future to find premium sales, and pulls them forward by 1-3 turns, logging the exact debt to repay later. It does not try to guess the opponent's shed state.

## Status of V057
V057 remains the VERIFIED LOCAL CHAMPION against our previous baselines (`main.py`, `V025-A`, `V085`), but it is fundamentally an ~1100-tier agent. Its base trace is inefficient (HIRE5 vs HIRE4), and its market logic (blind front-running without demand scaling) is actively harmful compared to the 3000+ meta.

The prior synthetic data has been entirely deprecated. Future experiments must only be derived from real public artifacts and controlled benchmarking.
