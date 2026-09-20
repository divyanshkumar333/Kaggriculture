"""
Resumable sequential benchmark harness for Kaggriculture.

Runs A vs B on both seats for each seed, checkpointing after every seed block.
Sequential execution (1 worker) to avoid OOM on memory-constrained machines.

Usage:
    python scripts/bench_resumable.py agents/v057_generalized_spoiler.py main.py \
        --pool validation --batch 8 --label_a V057 --label_b main

Features:
- TRUE CRN: same seed for both seat orderings (no offset)
- Per-seed-block checkpointing to CSV
- Resume from partial runs (skips already-completed seeds)
- Bootstrap CI over seed blocks (not individual games)
- W/T/L + win_score as primary statistic
- Cash delta as secondary
- Batch-mode: saves results_part_XX.csv after each batch
"""
import argparse, csv, importlib.util, json, math, os, random, statistics, sys, time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_one_game(agent_a_fn, agent_b_fn, seed, max_steps=720):
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": max_steps + 1, "randomSeed": seed}, debug=False)

    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"], "hands": [["PASS"] for _ in (farm.get("hands") or [])], "market": []}

    env.run([lambda obs, cfg, _a=agent_a_fn: _safe(_a, obs, cfg),
             lambda obs, cfg, _b=agent_b_fn: _safe(_b, obs, cfg)])
    final = env.steps[-1]
    return float(final[0].reward or 0), float(final[1].reward or 0)

def run_seed_block(agent_a_path, agent_b_path, seed):
    """Run both seats for one seed. Returns dict with all results."""
    agent_a = load_agent(agent_a_path)
    agent_b = load_agent(agent_b_path)

    t0 = time.perf_counter()

    # Seat 0: A=P0, B=P1
    r0a, r0b = run_one_game(agent_a, agent_b, seed)
    score0 = 1.0 if r0a > r0b else 0.5 if r0a == r0b else 0.0

    # Seat 1: B=P0, A=P1 — SAME seed (TRUE CRN)
    r1b, r1a = run_one_game(agent_b, agent_a, seed)
    score1 = 1.0 if r1a > r1b else 0.5 if r1a == r1b else 0.0

    elapsed = time.perf_counter() - t0

    return {
        "seed": seed,
        "seat0_cash_a": r0a, "seat0_cash_b": r0b, "seat0_result": score0,
        "seat1_cash_b": r1b, "seat1_cash_a": r1a, "seat1_result": score1,
        "block_win_score": (score0 + score1) / 2.0,
        "block_cash_delta": ((r0a - r0b) + (r1a - r1b)) / 2.0,
        "elapsed_s": round(elapsed, 1)
    }

CSV_FIELDS = ["seed", "seat0_cash_a", "seat0_cash_b", "seat0_result",
              "seat1_cash_b", "seat1_cash_a", "seat1_result",
              "block_win_score", "block_cash_delta", "elapsed_s"]

def load_completed_seeds(csv_path):
    """Load seeds already completed from checkpoint CSV."""
    done = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add(int(row["seed"]))
    return done

def append_result(csv_path, result, write_header=False):
    """Append one result row to checkpoint CSV."""
    mode = "w" if write_header else "a"
    with open(csv_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(result)

def load_all_results(csv_path):
    """Load all results from checkpoint CSV."""
    results = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({k: float(v) if k != "seed" else int(v) for k, v in row.items()})
    return results

def bootstrap_ci(data, n_boot=2000, alpha=0.05):
    if len(data) < 2:
        return min(data), max(data) if data else (0.0, 0.0)
    boots = sorted(sum(random.choices(data, k=len(data))) / len(data) for _ in range(n_boot))
    return boots[int(alpha / 2 * n_boot)], boots[int((1 - alpha / 2) * n_boot)]

def summarize(results, label_a, label_b, pool, start_seed):
    """Compute and print summary statistics."""
    n_seeds = len(results)
    W = T = L = 0
    block_wins = []
    block_deltas = []

    for r in results:
        for s in (r["seat0_result"], r["seat1_result"]):
            if s == 1.0: W += 1
            elif s == 0.0: L += 1
            else: T += 1
        block_wins.append(r["block_win_score"])
        block_deltas.append(r["block_cash_delta"])

    total = n_seeds * 2
    win_score = (W + 0.5 * T) / total if total else 0

    ci_win_lo, ci_win_hi = bootstrap_ci(block_wins)
    ci_cash_lo, ci_cash_hi = bootstrap_ci(block_deltas)
    mean_delta = statistics.mean(block_deltas) if block_deltas else 0

    print(f"\n{'='*60}")
    print(f"  RESULT: {label_a} vs {label_b}")
    print(f"  Pool: {pool}  |  Seeds: {n_seeds}  |  Games: {total}")
    print(f"  W={W}  T={T}  L={L}")
    print(f"  Win Score: {win_score*100:.1f}%")
    print(f"  95% CI (Win Score): [{ci_win_lo*100:.1f}%, {ci_win_hi*100:.1f}%]")
    print(f"  Mean cash delta: {mean_delta:+.0f}")
    print(f"  95% CI (Cash Delta): [{ci_cash_lo:+.0f}, {ci_cash_hi:+.0f}]")
    print(f"{'='*60}\n")

    return {
        "agent_a": label_a, "agent_b": label_b,
        "pool": pool, "start_seed": start_seed,
        "seed_blocks": n_seeds, "total_games": total,
        "W": W, "T": T, "L": L,
        "win_score": round(win_score, 4),
        "ci_win_lo": round(ci_win_lo, 4), "ci_win_hi": round(ci_win_hi, 4),
        "mean_cash_delta": round(mean_delta, 2),
        "ci_cash_lo": round(ci_cash_lo, 2), "ci_cash_hi": round(ci_cash_hi, 2)
    }

def main():
    ap = argparse.ArgumentParser(description="Resumable sequential paired benchmark")
    ap.add_argument("agent_a", help="Path to agent A")
    ap.add_argument("agent_b", help="Path to agent B")
    ap.add_argument("--pool", choices=["discovery", "validation", "promotion", "custom"], default="validation")
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--batch", type=int, default=8, help="Seeds per checkpoint batch")
    ap.add_argument("--label_a", default=None)
    ap.add_argument("--label_b", default=None)
    ap.add_argument("--run_dir", default=None, help="Directory for checkpoints (auto-generated if not set)")
    args = ap.parse_args()

    label_a = args.label_a or Path(args.agent_a).stem
    label_b = args.label_b or Path(args.agent_b).stem
    agent_a_path = os.path.abspath(args.agent_a)
    agent_b_path = os.path.abspath(args.agent_b)

    # Seed pool
    pools = {"discovery": (10000, 64), "validation": (11000, 64), "promotion": (12000, 128)}
    if args.pool == "custom":
        start_seed = args.start or 9000
        n_seeds = args.seeds or 8
    else:
        start_seed, n_seeds = pools[args.pool]
        if args.start is not None: start_seed = args.start
        if args.seeds is not None: n_seeds = args.seeds

    seeds = list(range(start_seed, start_seed + n_seeds))

    # Run directory
    if args.run_dir:
        run_dir = args.run_dir
    else:
        run_dir = os.path.join(ROOT, "RESEARCH", "runs", f"{label_a}_vs_{label_b}_{args.pool}")
    os.makedirs(run_dir, exist_ok=True)

    checkpoint_csv = os.path.join(run_dir, "results.csv")
    done_seeds = load_completed_seeds(checkpoint_csv)
    remaining = [s for s in seeds if s not in done_seeds]

    print(f"\n{'='*60}")
    print(f"  BENCHMARK: {label_a} vs {label_b}")
    print(f"  Pool: {args.pool.upper()}")
    print(f"  Seeds: {seeds[0]}..{seeds[-1]}  ({n_seeds} blocks, {n_seeds*2} games)")
    print(f"  Already done: {len(done_seeds)}  |  Remaining: {len(remaining)}")
    print(f"  Batch size: {args.batch}")
    print(f"  Checkpoint: {checkpoint_csv}")
    print(f"  Mode: SEQUENTIAL (1 worker)")
    print(f"{'='*60}\n")

    if not remaining:
        print("All seeds already completed! Loading results for summary...")
        results = load_all_results(checkpoint_csv)
        summary = summarize(results, label_a, label_b, args.pool, start_seed)
        report_file = os.path.join(run_dir, "summary.json")
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to {report_file}")
        return 0

    # If first run, write CSV header
    write_header = not os.path.exists(checkpoint_csv) or os.path.getsize(checkpoint_csv) == 0

    batch_num = 0
    total_elapsed = 0
    games_done = len(done_seeds) * 2

    for i, seed in enumerate(remaining):
        t_start = time.perf_counter()
        result = run_seed_block(agent_a_path, agent_b_path, seed)
        elapsed = time.perf_counter() - t_start
        total_elapsed += elapsed
        games_done += 2

        # Print per-seed result
        s0c = "W" if result["seat0_result"] == 1.0 else "L" if result["seat0_result"] == 0.0 else "T"
        s1c = "W" if result["seat1_result"] == 1.0 else "L" if result["seat1_result"] == 0.0 else "T"
        completed = len(done_seeds) + i + 1
        pct = completed / n_seeds * 100
        avg_per_game = total_elapsed / (2 * (i + 1))
        eta_min = avg_per_game * (len(remaining) - i - 1) * 2 / 60

        print(f"  [{completed}/{n_seeds} {pct:.0f}%] Seed {seed}: "
              f"S0={result['seat0_cash_a']:.0f}v{result['seat0_cash_b']:.0f}[{s0c}] "
              f"S1={result['seat1_cash_b']:.0f}v{result['seat1_cash_a']:.0f}[{s1c}] "
              f"({elapsed:.0f}s, ETA {eta_min:.0f}m)")

        # Checkpoint immediately
        append_result(checkpoint_csv, result, write_header=write_header)
        write_header = False

        # Batch summary
        if (i + 1) % args.batch == 0:
            batch_num += 1
            all_results = load_all_results(checkpoint_csv)
            print(f"\n  --- Batch {batch_num} checkpoint ({len(all_results)}/{n_seeds} seeds) ---")
            partial = summarize(all_results, label_a, label_b, args.pool, start_seed)
            batch_file = os.path.join(run_dir, f"results_part_{batch_num:02d}.json")
            with open(batch_file, "w") as f:
                json.dump(partial, f, indent=2)
            print(f"  Saved {batch_file}\n")

    # Final summary
    all_results = load_all_results(checkpoint_csv)
    summary = summarize(all_results, label_a, label_b, args.pool, start_seed)
    report_file = os.path.join(run_dir, "summary.json")
    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Final summary saved to {report_file}")

    # Also save to reports/ for visibility
    reports_copy = os.path.join(ROOT, "reports", f"benchmark_{label_a}_vs_{label_b}.json")
    with open(reports_copy, "w") as f:
        json.dump(summary, f, indent=2)

    return 0 if summary["W"] > summary["L"] else 1

if __name__ == "__main__":
    sys.exit(main())
