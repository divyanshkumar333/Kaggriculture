import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from kaggle_environments import make

def _run_single_match(args):
    cand_path, opp_path, seed, cand_seat = args
    
    # Suppress C++ OpenSpiel import spam via OS-level FD redirection
    import os, sys
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stdout = os.dup(1)
        old_stderr = os.dup(2)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        from kaggle_environments import make
        os.dup2(old_stdout, 1)
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stdout)
        os.close(old_stderr)
    except Exception:
        from kaggle_environments import make

    # Load inside process to ensure clean isolation
    def load_code(p):
        ns = {}
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, os.path.basename(p), "exec"), ns)
        callables = [v for v in ns.values() if callable(v)]
        if not callables:
            raise ValueError(f"No callable found in {p}")
        return callables[-1]

    cand_agent = load_code(cand_path)
    opp_agent = load_code(opp_path)
    
    agents = [cand_agent, opp_agent] if cand_seat == 0 else [opp_agent, cand_agent]
    
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run(agents)
    
    last = env.steps[-1]
    cand_idx = cand_seat
    opp_idx = 1 - cand_seat
    
    r_cand = float(last[cand_idx].get("reward", 0) or 0)
    r_opp = float(last[opp_idx].get("reward", 0) or 0)
    s_cand = last[cand_idx].get("status", "UNKNOWN")
    s_opp = last[opp_idx].get("status", "UNKNOWN")
    
    margin = r_cand - r_opp
    win = 1 if margin > 0 else 0
    loss = 1 if margin < 0 else 0
    draw = 1 if margin == 0 else 0
    
    return {
        "opp": os.path.basename(opp_path),
        "seed": seed,
        "cand_seat": cand_seat,
        "cand_reward": r_cand,
        "opp_reward": r_opp,
        "margin": margin,
        "win": win,
        "loss": loss,
        "draw": draw,
        "s_cand": s_cand,
        "s_opp": s_opp
    }

def run_fast_tournament(cand_path, population_paths, seeds=[42, 101, 2024, 777, 9999], max_workers=6):
    print("=" * 65, flush=True)
    print(f"FAST PARALLEL TOURNAMENT", flush=True)
    print(f"Candidate: {os.path.basename(cand_path)}", flush=True)
    print(f"Population: {len(population_paths)} opponents", flush=True)
    print(f"Seeds: {len(seeds)} seeds ({len(seeds)*2} games per opponent)", flush=True)
    print(f"Total Matches: {len(population_paths) * len(seeds) * 2}", flush=True)
    print("=" * 65, flush=True)
    
    tasks = []
    for opp_path in population_paths:
        for seed in seeds:
            for seat in (0, 1):
                tasks.append((cand_path, opp_path, seed, seat))
                
    t0 = time.time()
    results_by_opp = {os.path.basename(p): [] for p in population_paths}
    
    completed = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_run_single_match, t): t for t in tasks}
        for f in as_completed(futures):
            res = f.result()
            results_by_opp[res["opp"]].append(res)
            completed += 1
            if completed % 10 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} matches done ({time.time()-t0:.1f}s)...", flush=True)
                
    elapsed = time.time() - t0
    print("-" * 65, flush=True)
    print(f"Completed in {elapsed:.1f}s ({elapsed/len(tasks):.2f}s per match across {max_workers} cores)", flush=True)
    print("=" * 65, flush=True)
    
    total_w = 0
    total_l = 0
    total_d = 0
    total_margin = 0
    total_games = 0
    
    summary = {}
    for opp, res_list in results_by_opp.items():
        w = sum(r["win"] for r in res_list)
        l = sum(r["loss"] for r in res_list)
        d = sum(r["draw"] for r in res_list)
        g = len(res_list)
        m = sum(r["margin"] for r in res_list) / g if g > 0 else 0
        wr = (w / g) * 100 if g > 0 else 0
        
        total_w += w
        total_l += l
        total_d += d
        total_games += g
        total_margin += sum(r["margin"] for r in res_list)
        
        cand_mean = sum(r["cand_reward"] for r in res_list) / g
        opp_mean = sum(r["opp_reward"] for r in res_list) / g
        
        print(f"vs {opp:30} | {w:2d}W - {l:2d}L - {d:2d}D ({wr:5.1f}%) | Cand: {cand_mean:7.0f} | Opp: {opp_mean:7.0f} | Margin: {m:+8.0f}", flush=True)
        summary[opp] = {"wins": w, "losses": l, "draws": d, "win_rate": wr, "cand_mean": cand_mean, "opp_mean": opp_mean, "margin": m}
        
    overall_wr = (total_w / total_games) * 100 if total_games > 0 else 0
    overall_margin = total_margin / total_games if total_games > 0 else 0
    print("=" * 65, flush=True)
    print(f"OVERALL: {total_w}W - {total_l}L - {total_d}D ({overall_wr:5.1f}%) | Mean Margin: {overall_margin:+8.0f}", flush=True)
    print("=" * 65, flush=True)
    
    return summary, overall_wr, overall_margin

if __name__ == "__main__":
    cand = sys.argv[1] if len(sys.argv) > 1 else r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    pop = [
        r"e:\Setup\kaggle\kaggriculture\submission_v057_control.py",
        r"e:\Setup\kaggle\kaggriculture\agents\public_v16_rc5.py",
        r"e:\Setup\kaggle\kaggriculture\agents\013_robust_trace.py",
        r"e:\Setup\kaggle\kaggriculture\agents\v081_kaggle_83k_trace.py"
    ]
    run_fast_tournament(cand, pop, seeds=[42, 101, 2024, 777, 9999], max_workers=6)
