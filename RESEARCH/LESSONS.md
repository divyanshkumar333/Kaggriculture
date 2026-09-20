# Kaggriculture Autoresearch Lessons Ledger

## Meta-Rule
Every 5 accepted improvements, summarize durable lessons here.

---

## Session 1 Lessons (Cycle Start — 2026-09-20)

### L001: The Front-Run Mechanism is Load-Bearing
EXP-004 proved: removing front-run entirely = 0% win rate.
EXP-006 proved: removing repay = 13.5% win rate.
Neither can be simplified without full regression.

### L002: Lookahead Depth Has Diminishing Returns Past 30 Steps
EXP-021 through EXP-024 sweeping depth 24/30/36/48 show +$62k margin all within noise.
Depth 30 (V051) selected as baseline. Do not re-sweep without a new mechanic.

### L003: Hungarian Matching is Not Yet Proven Superior to Greedy
The CONTRADICTIONS.md audit shows the labor paradox is unresolved.
No promotion should claim "Hungarian is better than greedy" without a paired comparison.

### L004: Documentation Titles Cannot Be Trusted
V099 was labeled "Bayesian Adaptive Master" but contains no Bayesian inference.
V026 "Golden Ratio" contains no golden ratio. Always read the code.

### L005: Opponent Cow Count is a Weak Single Feature
The V099 threshold `opp_cows >= 3` is only tested at Day 6.
No evidence it produces better policy than ignoring opponent entirely.
HYPOTHESIS: A richer opponent feature set using visible market deltas would be stronger.

### L006: main.py is the True Champion
champion_history.md records V036 (lookahead8) as local champ.
main.py decoded trace is the V032 lineage same architecture family.
The git log shows main.py was most recently updated.
Both need fresh verification against each other on frozen seeds.

### L007: V099 Must Not Be Submitted Without Benchmark
V099 uses scipy which adds a dependency. The main.py trace-replay has no external deps.
Scipy dependency risk at Kaggle eval time is real.

### L008: Replay-Seed Agents (V092b) are Deterministic Single-Strategy
V092b is a pure trace-replay from one high-score game. It has no adaptation.
Useful as opponent but not as champion candidate without seat-pair ablation.

### L009: Champion is Already an Optimal Terminal Liquidator
Attempts to override main.py's terminal phase (Day 25+) with manual dumping or holding (EXP-036 series) consistently lose by -. The champion's combination of _front_run (which pulls future trace sales to the moment of harvest) and _rank_sell_slots acts as a perfect continuous liquidator. Manually overriding the trace's HIRE or CARE actions in the terminal phase causes unharvested yield to rot, resulting in a net loss.
