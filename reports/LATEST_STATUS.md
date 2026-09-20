# Kaggriculture Autoresearch - Latest Status

## Current Champion
**Agent:** main.py (V103_PrisonResolution)
**Lineage:** V032 -> V103
**Date Promoted:** 2026-09-20
**Key Mechanics:**
- Trace-locked macro sequence (V032 actions string).
- Dynamic Sell Ranking (_rank_sell_slots) targeting highest un-crashed price.
- Strict Depth-2 Trace Front-Running (to exploit symmetric trace dynamics and wait out town consumption).
- NO Opponent Panic Selling (resolves symmetric Prisoner's Dilemma).

## Recent Discoveries (LESSONS.md)
1. **The Front-Run Mechanism is Load-Bearing**: _front_run is essential. Stripping it loses ~ against the baseline.
2. **Champion is Already an Optimal Terminal Liquidator**: main.py efficiently dumps its shed upon harvest using future trace sales. Any attempt to manually override terminal phase (Days 25+) with simpler logic loses - due to unharvested yield rotting.
3. **The Symmetric Prisoner's Dilemma (Panic Selling)**: When playing a trace-locked opponent, a deep lookahead (e.g. 30 steps) combined with opponent-panic-selling causes the agent to dump goods too early, subsidizing town consumption for the opponent. Strictly limiting lookahead to 2 steps and disabling panic selling completely resolves this, yielding +,831 vs baseline and + vs public_v16_rc5.

## Next Steps
The champion has successfully resolved its most critical known weakness (the -.5k Prisoner's Dilemma against public_v16_rc5).
Future experiments should focus on:
- Exploring whether adjusting the opening budget overflow (from EXP-035b) can further boost the trace macro without breaking synchronization.
- Finding opportunities to dynamically purchase assets (like additional seeds or animals) in response to opponent macro deviations, if any budget slack can be safely extracted.
