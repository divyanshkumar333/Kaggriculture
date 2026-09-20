# External Research Library

Date: 2026-09-20

## Sources Identified

### A. Kaito Fukami — v27 Midgame Meta Reset (public score: 3090.1)
- Source: Kaggle public notebook
- Key mechanisms:
  1. Strict-future observability constraint (no future actions peeking)
  2. Observable event branching (locks route on first divergence)
  3. Meta reset at midgame: evaluates whether current route is still optimal
  4. Price-impact ordering (same as our impact ranking)
  5. Order-slot safety (max 10 market orders enforced)
  6. Route freshness: periodic re-evaluation of macro route
- What it teaches: Observable branching > single-trace replay; meta-reset improves adaptability
- Reproduced locally: NO (proprietary trace)
- Adapted: Opponent-shed inference (similar technique, independently implemented in main.py)

### B. Kaito Fukami — v48 Fast Routes (40/40 early floor)
- Key additions over v27:
  1. Sparse closed-loop routes (fewer total actions but higher per-action value)
  2. Execution diagnosis (detects action failures in prior turns)
  3. Lineage-safe evaluation (does not promote if route purity is broken)
- What it teaches: Route compactness matters; diagnose execution failures
- Status: Not yet adapted

### C. Barnyard Economist (Roman Rozen)
- Key mechanisms:
  1. Queue-aware farming: tasks queued by deadline, not by priority
  2. Route preservation: once a macro is chosen, execution doesn't switch
  3. Decision-edge improvements: only acts on information CHANGES
  4. Production atlas: pre-computed yield schedules
  5. Terminal behavior: explicit sell-all sequence starting turn 600
- What it teaches: Deadline-aware scheduling >> Hungarian arbitrary matching

### D. Meta Research
- Competition deadline: September 30, 2026
- Top known score: 3090.1 (Kaito Fukami)
- RL approaches: PPO/JAX (10k steps/sec) used by some top agents
- Key insights from web search:
  - "opening feed denial" is a known technique
  - "one-turn fertilizer preemption" is a known technique
  - Replay hunting is popular
  - Market timing (sell sequencing) is key differentiator

## Priority Adapter List

1. Terminal liquidation controller (EXP-036) — HIGH value, low compute
2. Observable event branching / meta reset (EXP-037) — HIGH value, medium compute
3. Queue-aware deadline scheduling (EXP-038) — MEDIUM value, medium compute
4. Fertilizer preemption (EXP-039) — LOW compute, potentially high value vs specific opponents
5. RL/PPO — LOWEST priority (do not attempt without prior experiments)
