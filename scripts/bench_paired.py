"""
Sequential and parallel paired benchmark harness.
Usage:
    python scripts/bench_paired.py <agent_a_file> <agent_b_file> --seeds 8 --start 9000 --workers 4

Both seats tested: seed S -> A vs B, B vs A.
Reports W/T/L, win_score, mean cash delta, 95% bootstrap CI.
"""
import argparse, importlib.util, json, math, random, sys, traceback, os
from pathlib import Path
import concurrent.futures

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
            # Silence exception printing to keep progress bar clean
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
    r1b, r1a = run_game_process(path_b, path_a, seed + 1000000, max_steps)
    return seed, r0a, r0b, r1a, r1b

def bootstrap_ci(data, n_boot=2000, alpha=0.05):
    if not data:
        return 0, 0
    boots = [sum(random.choices(data, k=len(data)))/len(data) for _ in range(n_boot)]
    boots.sort()
    lo = boots[int(alpha / 2 * n_boot)]
    hi = boots[int((1 - alpha / 2) * n_boot)]
    return lo, hi

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_a")
    ap.add_argument("agent_b")
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--start", type=int, default=9000)
    ap.add_argument("--label_a", default=None)
    ap.add_argument("--label_b", default=None)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    label_a = args.label_a or Path(args.agent_a).stem
    label_b = args.label_b or Path(args.agent_b).stem
    
    agent_a_path = os.path.abspath(args.agent_a)
    agent_b_path = os.path.abspath(args.agent_b)

    seeds = list(range(args.start, args.start + args.seeds))
    W = T = L = 0
    deltas = []

    print(f"\n{'='*60}")
    print(f"  BENCHMARK: {label_a} vs {label_b}")
    print(f"  Seeds: {seeds[0]}..{seeds[-1]}  ({args.seeds} pairs, {args.seeds*2} matches)")
    print(f"  Workers: {args.workers}")
    print(f"{'='*60}\n")

    tasks = [(agent_a_path, agent_b_path, s, 720) for s in seeds]
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for seed, r0a, r0b, r1a, r1b in executor.map(_worker_wrapper, tasks):
            cash_a = (r0a + r1a) / 2
            cash_b = (r0b + r1b) / 2
            delta = cash_a - cash_b
            deltas.append(delta)

            if cash_a > cash_b:
                W += 1; result = "W"
            elif cash_a < cash_b:
                L += 1; result = "L"
            else:
                T += 1; result = "T"

            print(f"  Seed {seed:6d}: A=${cash_a:9.0f}  B=${cash_b:9.0f}  d={delta:+10.0f}  [{result}]")

    mean_delta = sum(deltas) / len(deltas)
    win_score = W / args.seeds
    ci_lo, ci_hi = bootstrap_ci(deltas)

    print(f"\n{'='*60}")
    print(f"  RESULT: W={W}  T={T}  L={L}  (pairs: {args.seeds})")
    print(f"  Paired win rate: {win_score*100:.1f}%")
    print(f"  Mean cash delta: {mean_delta:+.0f}")
    print(f"  95% CI: [{ci_lo:+.0f}, {ci_hi:+.0f}]")
    print(f"{'='*60}\n")

    out = {"agent_a": label_a, "agent_b": label_b,
           "seeds": args.seeds, "seed_start": args.start,
           "W": W, "T": T, "L": L,
           "paired_win_rate": round(win_score, 4),
           "mean_delta": round(mean_delta, 2),
           "ci_lo": round(ci_lo, 2), "ci_hi": round(ci_hi, 2)}
    print(json.dumps(out, indent=2))
    return 0 if W > L else 1

if __name__ == "__main__":
    sys.exit(main())
