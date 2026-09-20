"""
Sequential and parallel paired benchmark harness.
Usage:
    python scripts/bench_paired.py <agent_a_file> <agent_b_file> --pool validation --workers 4

Both seats tested: seed S -> A vs B, B vs A using TRUE CRN (identical seed S).
Reports W/T/L, win_score, mean cash delta, and 95% bootstrap CI over seed blocks.
"""
import argparse, importlib.util, json, math, random, sys, traceback, os
from pathlib import Path
import concurrent.futures
import statistics

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_game_process(agent_a_path, agent_b_path, seed, max_steps=720):
    from kaggle_environments import make
    agent_a = load_agent(agent_a_path)
    agent_b = load_agent(agent_b_path)
    env = make("kaggriculture", configuration={"episodeSteps": max_steps + 1, "randomSeed": seed}, debug=False)
    
    def _safe(fn, obs, cfg):
        try:
            return fn(obs)
        except Exception:
            farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
            return {"farmer": ["PASS"],
                    "hands": [["PASS"] for _ in (farm.get("hands") or [])],
                    "market": []}
                    
    env.run([lambda obs, cfg, _a=agent_a: _safe(_a, obs, cfg),
             lambda obs, cfg, _b=agent_b: _safe(_b, obs, cfg)])
    final = env.steps[-1]
    r0 = final[0].reward or 0
    r1 = final[1].reward or 0
    return float(r0), float(r1)

def _worker_wrapper(args):
    path_a, path_b, seed, max_steps = args
    r0a, r0b = run_game_process(path_a, path_b, seed, max_steps)
    # TRUE CRN: Use the EXACT same seed without offset
    r1b, r1a = run_game_process(path_b, path_a, seed, max_steps)
    
    score1 = 1.0 if r0a > r0b else 0.5 if r0a == r0b else 0.0
    score2 = 1.0 if r1a > r1b else 0.5 if r1a == r1b else 0.0
    block_win_score = (score1 + score2) / 2.0
    
    delta1 = r0a - r0b
    delta2 = r1a - r1b
    block_cash_delta = (delta1 + delta2) / 2.0
    
    return {
        "seed": seed,
        "seat0_a": r0a, "seat0_b": r0b, "score1": score1, "delta1": delta1,
        "seat1_b": r1b, "seat1_a": r1a, "score2": score2, "delta2": delta2,
        "block_win_score": block_win_score,
        "block_cash_delta": block_cash_delta,
        "cash_a_values": [r0a, r1a],
        "cash_b_values": [r0b, r1b]
    }

def bootstrap_ci(data, n_boot=2000, alpha=0.05):
    if not data:
        return 0.0, 0.0
    boots = [sum(random.choices(data, k=len(data)))/len(data) for _ in range(n_boot)]
    boots.sort()
    lo = boots[int(alpha / 2 * n_boot)]
    hi = boots[int((1 - alpha / 2) * n_boot)]
    return lo, hi

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_a")
    ap.add_argument("agent_b")
    ap.add_argument("--pool", type=str, choices=["discovery", "validation", "promotion", "custom"], default="validation")
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--label_a", default=None)
    ap.add_argument("--label_b", default=None)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    label_a = args.label_a or Path(args.agent_a).stem
    label_b = args.label_b or Path(args.agent_b).stem
    
    agent_a_path = os.path.abspath(args.agent_a)
    agent_b_path = os.path.abspath(args.agent_b)

    # Define Disjoint Pools
    if args.pool == "discovery":
        start_seed = 10000
        n_seeds = 64
    elif args.pool == "validation":
        start_seed = 11000
        n_seeds = 64
    elif args.pool == "promotion":
        start_seed = 12000
        n_seeds = 128
    else: # custom
        start_seed = args.start if args.start is not None else 9000
        n_seeds = args.seeds if args.seeds is not None else 8

    if args.start is not None and args.pool != "custom":
        start_seed = args.start
    if args.seeds is not None and args.pool != "custom":
        n_seeds = args.seeds

    seeds = list(range(start_seed, start_seed + n_seeds))
    
    print(f"\n{'='*60}")
    print(f"  BENCHMARK: {label_a} vs {label_b}")
    print(f"  Pool: {args.pool.upper()}")
    print(f"  Seeds: {seeds[0]}..{seeds[-1]}  ({n_seeds} blocks, {n_seeds*2} games)")
    print(f"  Workers: {args.workers}")
    print(f"{'='*60}\n")

    tasks = [(agent_a_path, agent_b_path, s, 720) for s in seeds]
    
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for res in executor.map(_worker_wrapper, tasks):
            results.append(res)
            
            s1_char = "W" if res["score1"] == 1.0 else "L" if res["score1"] == 0.0 else "T"
            s2_char = "W" if res["score2"] == 1.0 else "L" if res["score2"] == 0.0 else "T"
            
            print(f"  Seed {res['seed']:6d}:  Seat0(A vs B): {res['seat0_a']:7.0f} vs {res['seat0_b']:7.0f} [{s1_char}]  |  Seat1(B vs A): {res['seat1_b']:7.0f} vs {res['seat1_a']:7.0f} [{s2_char}]")

    W = T = L = 0
    all_cash_a = []
    block_win_scores = []
    block_cash_deltas = []

    for r in results:
        for score in (r["score1"], r["score2"]):
            if score == 1.0: W += 1
            elif score == 0.0: L += 1
            else: T += 1
        all_cash_a.extend(r["cash_a_values"])
        block_win_scores.append(r["block_win_score"])
        block_cash_deltas.append(r["block_cash_delta"])

    total_games = n_seeds * 2
    win_score = (W + 0.5 * T) / total_games
    mean_cash_delta = sum(block_cash_deltas) / n_seeds
    
    # Paired Bootstrap over SEED BLOCKS
    ci_win_lo, ci_win_hi = bootstrap_ci(block_win_scores)
    ci_cash_lo, ci_cash_hi = bootstrap_ci(block_cash_deltas)
    
    all_cash_a.sort()
    mean_cash = statistics.mean(all_cash_a)
    median_cash = statistics.median(all_cash_a)
    p25 = all_cash_a[len(all_cash_a)//4]
    p75 = all_cash_a[3*len(all_cash_a)//4]
    cash_volatility = statistics.stdev(all_cash_a) if len(all_cash_a) > 1 else 0

    print(f"\n{'='*60}")
    print(f"  RESULT: W={W}  T={T}  L={L}  (out of {total_games} games)")
    print(f"  Win Score (win_rate): {win_score*100:.1f}%")
    print(f"  95% CI (Win Score): [{ci_win_lo*100:.1f}%, {ci_win_hi*100:.1f}%]")
    print(f"  Mean paired cash margin: {mean_cash_delta:+.0f}")
    print(f"  95% CI (Cash Margin): [{ci_cash_lo:+.0f}, {ci_cash_hi:+.0f}]")
    print(f"")
    print(f"  Secondary Agent A stats:")
    print(f"  Mean cash: ${mean_cash:.0f}  Median: ${median_cash:.0f}")
    print(f"  P25: ${p25:.0f}  P75: ${p75:.0f}  Vol: ${cash_volatility:.0f}")
    print(f"{'='*60}\n")

    out = {
        "agent_a": label_a, 
        "agent_b": label_b,
        "pool": args.pool,
        "seed_blocks": n_seeds, 
        "start_seed": start_seed,
        "total_games": total_games,
        "W": W, "T": T, "L": L,
        "win_score": round(win_score, 4),
        "ci_win_lo": round(ci_win_lo, 4),
        "ci_win_hi": round(ci_win_hi, 4),
        "mean_cash_delta": round(mean_cash_delta, 2),
        "ci_cash_lo": round(ci_cash_lo, 2),
        "ci_cash_hi": round(ci_cash_hi, 2)
    }
    
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    report_file = os.path.join(ROOT, "reports", f"benchmark_{label_a}_{label_b}.json")
    with open(report_file, "w") as f:
        json.dump(out, f, indent=2)
        
    print(json.dumps(out, indent=2))
    return 0 if W > L else 1

if __name__ == "__main__":
    sys.exit(main())
