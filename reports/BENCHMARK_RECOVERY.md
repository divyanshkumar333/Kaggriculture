# Benchmark Recovery Report
**Date:** 2026-09-20T17:38 IST  
**Recovery performed by:** Antigravity agent

## What Stalled

The Phase 5 autoresearch loop was stuck in `BENCHMARK_INTEGRITY_CHECK` / `CORRECTING` state
for 2+ hours. The autoresearch state file (`RESEARCH/autoresearch/state.json`) shows:

```json
{
  "current_phase": "BENCHMARK_INTEGRITY_CHECK",
  "integrity_status": "CORRECTING",
  "experiments_run": 0
}
```

**No benchmark processes were actually running.** Zero Python, Kaggle, or background
tasks were alive when recovery began.

## Why It Stalled

1. **All processes died silently.** No python.exe, pythonw.exe, or kaggle.exe processes
   were running at recovery time (17:33 IST).
2. **Memory pressure.** The machine has only 7.4 GB total RAM with ~500 MB free at
   recovery time. The previous benchmark harness (`bench_paired.py`) defaults to
   `os.cpu_count() = 8` ProcessPoolExecutor workers. Each kaggle-environments game
   consumes ~228 MB peak RAM. 8 workers × 228 MB = ~1.8 GB additional RAM on top of
   baseline usage — likely OOM-killed or deadlocked on Windows.
3. **No checkpointing.** The existing `bench_paired.py` collects all results in memory
   and only writes output at the end. Any crash = total loss of progress.
4. **The autoresearch state machine got stuck.** It entered `CORRECTING` but the
   correction process (the benchmark) died, leaving the state file in limbo with no
   recovery mechanism.

## Which Processes Were Killed

**None.** No processes were running. Only cmd.exe shells (from Antigravity IDE) were present.

## Partial Results Preserved

No partial benchmark results existed to preserve. The `experiments.csv` has only headers.
The `RESEARCH/benchmark_history/` contains 76 historical benchmark JSONs from earlier
phases (V029-V055 era) — all preserved, untouched.

## Micro-Benchmark Results

Ran V057 vs main.py on the validation pool to calibrate timing:

| Metric | Value |
|--------|-------|
| Single game wall-clock | 38.5s |
| Single game peak RAM | 228 MB |
| 4-game sequential | 108.2s (27.0 s/game) |
| 4-game peak RAM | 111 MB |
| Games/hour (sequential) | 133 |
| Est 128 games (64 seeds × 2 seats) | ~58 min |
| Est 384 games (3 matchups × 64 seeds × 2 seats) | ~173 min |

### Micro-benchmark game results (seeds 11000-11003, V057 as P0):
| Seed | V057 | main.py | Winner |
|------|------|---------|--------|
| 11000 | 115,520 | 116,734 | main.py |
| 11001 | 115,237 | 117,362 | main.py |
| 11002 | 123,183 | 118,411 | V057 |
| 11003 | 92,919 | 88,530 | V057 |

## Chosen Worker Count

**1 worker (sequential execution).**

Rationale:
- 500 MB free RAM cannot support even 2 concurrent kaggle-environments instances safely
- Sequential mode measured at 27 s/game = 133 games/hour — adequate for 64-seed runs
- Each 64-seed matchup completes in ~58 minutes — acceptable
- No risk of OOM, deadlock, or OpenBLAS thread contention

## Correctness Checks

### Same-seed seat swap ✅
The `bench_resumable.py` harness uses TRUE CRN:
- Game 1: `run_one_game(agent_a, agent_b, seed)` — A=P0, B=P1
- Game 2: `run_one_game(agent_b, agent_a, seed)` — B=P0, A=P1  
- **Same seed, no offset**

### W/T/L scoring ✅
Each game independently scored: W=1.0, T=0.5, L=0.0
Win Score = (W + 0.5×T) / total_games

### Bootstrap over seed blocks ✅
CI computed over per-seed block averages, not individual games.

### Checkpointing ✅
- Results written to CSV after EVERY seed block
- Resume from partial runs (skips completed seeds)
- Batch summaries saved every 8 seeds as `results_part_XX.json`
- Each matchup has its own `RESEARCH/runs/<run_id>/` directory

### No shared mutable state ✅
Each benchmark run writes to its own directory under `RESEARCH/runs/`.

## Estimated Full Benchmark Runtime

| Matchup | Seeds | Games | Est. Time |
|---------|-------|-------|-----------|
| V057 vs main.py | 64 | 128 | ~58 min |
| V057 vs V025-A | 64 | 128 | ~58 min |
| V057 vs V085 | 64 | 128 | ~58 min |
| **Total** | **192** | **384** | **~174 min (~3 hours)** |

Matchups run sequentially (not simultaneously) to avoid resource contention.

## Next Benchmark Command

```bash
# Run sequentially, one matchup at a time:

# 1. V057 vs main.py (validation pool, 64 seeds, batch 8) - DONE
# Results: 101 W, 0 T, 27 L. Win Score 78.91% [95% CI: 71.88% - 85.16%]. Mean cash delta: +1440.79

# 2. V057 vs V025-A - DONE
# Results: 128 W, 0 T, 0 L. Win Score 100.0% [95% CI: 100.0% - 100.0%]. Mean cash delta: +65720.92
python scripts/bench_resumable.py agents/v057_generalized_spoiler.py agents/v025_a_aggressive_cows.py --pool validation --batch 8 --label_a V057 --label_b V025-A

# 3. V057 vs V085 - DONE
# Results: 128 W, 0 T, 0 L. Win Score 100.0% [95% CI: 100.0% - 100.0%]. Mean cash delta: +122029.27
python scripts/bench_resumable.py agents/v057_generalized_spoiler.py agents/v085_grandmaster_roi.py --pool validation --batch 8 --label_a V057 --label_b V085
```

## Champion Safety

- V057 remains **PROVISIONAL** champion
- main.py is **UNTOUCHED**
- V025-A (`agents/v025_a_aggressive_cows.py`) is **UNTOUCHED**
- V085 (`agents/v085_grandmaster_roi.py`) is **UNTOUCHED**
- No new strategy experiments (EXP-036, V101-V112, PPO, etc.) will run until benchmarks complete

## Recovery Status

| Check | Status |
|-------|--------|
| Benchmark runs reliably | ✅ (micro-benchmark completed 5 games without crash) |
| Progress is visible | ✅ (per-seed progress printed with ETA) |
| Partial results checkpointed | ✅ (CSV written after every seed) |
| Same-seed seat swap correct | ✅ (TRUE CRN, no offset) |
| W/T/L calculated correctly | ✅ (per-game scoring, block bootstrap) |
| No process stalled | ✅ (all dead processes identified, no orphans) |
| Final result reproducible | ✅ (deterministic seeds, checkpointed results) |
