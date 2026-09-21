import os
import sys
import time
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

def _run_single_match(args):
    p0_path, p1_path, seed = args
    
    from kaggle_environments import make

    def load_code(p):
        ns = {}
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, os.path.basename(p), "exec"), ns)
        callables = [v for v in ns.values() if callable(v)]
        return callables[-1]

    agent0 = load_code(p0_path)
    agent1 = load_code(p1_path)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([agent0, agent1])

    # Telemetry: calculate final cash, market sales revenue, premium sales revenue
    PREMIUMS = {"STRAWBERRY", "MELON", "MILK", "WOOL"}
    p0_sales = 0.0
    p1_sales = 0.0
    p0_prem = 0.0
    p1_prem = 0.0

    steps = env.steps
    for s in steps[:-1]:
        obs0 = s[0]["observation"]
        prices = obs0.get("market", {}).get("prices", {})

        act0 = s[0].get("action") or {}
        if isinstance(act0, dict):
            for o in act0.get("market", []):
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    val = prices.get(o[1], 1) * o[2]
                    p0_sales += val
                    if o[1] in PREMIUMS:
                        p0_prem += val

        act1 = s[1].get("action") or {}
        if isinstance(act1, dict):
            for o in act1.get("market", []):
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    val = prices.get(o[1], 1) * o[2]
                    p1_sales += val
                    if o[1] in PREMIUMS:
                        p1_prem += val

    final = env.steps[-1]
    r0 = float(final[0].get("reward", 0) or 0)
    r1 = float(final[1].get("reward", 0) or 0)

    return {
        "p0": os.path.basename(p0_path),
        "p1": os.path.basename(p1_path),
        "seed": seed,
        "r0": r0,
        "r1": r1,
        "p0_sales": p0_sales,
        "p1_sales": p1_sales,
        "p0_prem": p0_prem,
        "p1_prem": p1_prem
    }

def main():
    ctrl = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    quote = r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py"
    
    opponents = [
        r"e:\Setup\kaggle\kaggriculture\submission_v057_control.py",
        r"e:\Setup\kaggle\kaggriculture\agents\public_v16_rc5.py",
        r"e:\Setup\kaggle\kaggriculture\agents\013_robust_trace.py",
        r"e:\Setup\kaggle\kaggriculture\agents\v081_kaggle_83k_trace.py"
    ]

    seeds = [42, 101, 2024, 777, 9999, 123, 456, 789] # 8 diverse seeds x 2 seats = 16 matches per pairing

    tasks = []
    # 1. H2H tasks (Quote vs Control)
    for s in seeds:
        tasks.append((quote, ctrl, s))
        tasks.append((ctrl, quote, s))

    # 2. Candidate vs Population tasks (Exact paired seeds/seats)
    for opp in opponents:
        for s in seeds:
            # Control
            tasks.append((ctrl, opp, s))
            tasks.append((opp, ctrl, s))
            # Quote Priority
            tasks.append((quote, opp, s))
            tasks.append((opp, quote, s))

    print(f"Total Matches to execute: {len(tasks)} across 6 CPU workers...")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_run_single_match, t): t for t in tasks}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            results.append(res)
            completed += 1
            if completed % 10 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} matches ({time.time()-t0:.1f}s)...", flush=True)

    elapsed = time.time() - t0
    print(f"Completed in {elapsed:.1f}s ({elapsed/len(tasks):.2f}s per match)")

    # 1. Analyze H2H: Quote vs Control
    h2h_q_wins, h2h_c_wins, h2h_draws = 0, 0, 0
    q_cash_h2h, c_cash_h2h = [], []
    q_prem_h2h, c_prem_h2h = [], []
    q_sales_h2h, c_sales_h2h = [], []

    for r in results:
        if r["p0"] == "v104_quote_priority.py" and r["p1"] == "the_2945_farm.py":
            q_cash_h2h.append(r["r0"])
            c_cash_h2h.append(r["r1"])
            q_prem_h2h.append(r["p0_prem"])
            c_prem_h2h.append(r["p1_prem"])
            q_sales_h2h.append(r["p0_sales"])
            c_sales_h2h.append(r["p1_sales"])
            if r["r0"] > r["r1"]: h2h_q_wins += 1
            elif r["r1"] > r["r0"]: h2h_c_wins += 1
            else: h2h_draws += 1
        elif r["p0"] == "the_2945_farm.py" and r["p1"] == "v104_quote_priority.py":
            c_cash_h2h.append(r["r0"])
            q_cash_h2h.append(r["r1"])
            c_prem_h2h.append(r["p0_prem"])
            q_prem_h2h.append(r["p1_prem"])
            c_sales_h2h.append(r["p0_sales"])
            q_sales_h2h.append(r["p1_sales"])
            if r["r1"] > r["r0"]: h2h_q_wins += 1
            elif r["r0"] > r["r1"]: h2h_c_wins += 1
            else: h2h_draws += 1

    h2h_n = len(q_cash_h2h)
    print("\n" + "=" * 70)
    print("TASK 3: CAUSAL VALIDATION REPORT — HEAD-TO-HEAD")
    print("=" * 70)
    print(f"Matches: {h2h_n} (8 paired seeds x 2 seats)")
    print(f"V104 Quote Priority: {h2h_q_wins} W ({h2h_q_wins/h2h_n*100:.1f}%)")
    print(f"V104 Control (2945): {h2h_c_wins} W ({h2h_c_wins/h2h_n*100:.1f}%)")
    print(f"Draws:               {h2h_draws} D ({h2h_draws/h2h_n*100:.1f}%)")
    print("-" * 70)
    print(f"Final Cash Mean:     Quote=${np.mean(q_cash_h2h):,.0f} | Ctrl=${np.mean(c_cash_h2h):,.0f} | Delta=${np.mean(q_cash_h2h)-np.mean(c_cash_h2h):+,.0f}")
    print(f"Final Cash Median:   Quote=${np.median(q_cash_h2h):,.0f} | Ctrl=${np.median(c_cash_h2h):,.0f}")
    print(f"Final Cash Variance: Quote={np.var(q_cash_h2h):,.0f} | Ctrl={np.var(c_cash_h2h):,.0f}")
    print(f"Market Revenue Mean: Quote=${np.mean(q_sales_h2h):,.0f} | Ctrl=${np.mean(c_sales_h2h):,.0f} | Delta=${np.mean(q_sales_h2h)-np.mean(c_sales_h2h):+,.0f}")
    print(f"Premium Rev Mean:    Quote=${np.mean(q_prem_h2h):,.0f} | Ctrl=${np.mean(c_prem_h2h):,.0f} | Delta=${np.mean(q_prem_h2h)-np.mean(c_prem_h2h):+,.0f}")

    # 2. Analyze vs Population
    c_pop_w, c_pop_l, c_pop_d = 0, 0, 0
    q_pop_w, q_pop_l, q_pop_d = 0, 0, 0
    c_pop_cash, q_pop_cash = [], []
    c_pop_prem, q_pop_prem = [], []
    c_pop_sales, q_pop_sales = [], []

    for opp in opponents:
        opp_name = os.path.basename(opp)
        for s in seeds:
            # P0 matches
            c_r0 = [r for r in results if r["p0"] == "the_2945_farm.py" and r["p1"] == opp_name and r["seed"] == s][0]
            q_r0 = [r for r in results if r["p0"] == "v104_quote_priority.py" and r["p1"] == opp_name and r["seed"] == s][0]

            c_pop_cash.append(c_r0["r0"])
            q_pop_cash.append(q_r0["r0"])
            c_pop_prem.append(c_r0["p0_prem"])
            q_pop_prem.append(q_r0["p0_prem"])
            c_pop_sales.append(c_r0["p0_sales"])
            q_pop_sales.append(q_r0["p0_sales"])

            if c_r0["r0"] > c_r0["r1"]: c_pop_w += 1
            elif c_r0["r0"] < c_r0["r1"]: c_pop_l += 1
            else: c_pop_d += 1

            if q_r0["r0"] > q_r0["r1"]: q_pop_w += 1
            elif q_r0["r0"] < q_r0["r1"]: q_pop_l += 1
            else: q_pop_d += 1

            # P1 matches
            c_r1 = [r for r in results if r["p1"] == "the_2945_farm.py" and r["p0"] == opp_name and r["seed"] == s][0]
            q_r1 = [r for r in results if r["p1"] == "v104_quote_priority.py" and r["p0"] == opp_name and r["seed"] == s][0]

            c_pop_cash.append(c_r1["r1"])
            q_pop_cash.append(q_r1["r1"])
            c_pop_prem.append(c_r1["p1_prem"])
            q_pop_prem.append(q_r1["p1_prem"])
            c_pop_sales.append(c_r1["p1_sales"])
            q_pop_sales.append(q_r1["p1_sales"])

            if c_r1["r1"] > c_r1["r0"]: c_pop_w += 1
            elif c_r1["r1"] < c_r1["r0"]: c_pop_l += 1
            else: c_pop_d += 1

            if q_r1["r1"] > q_r1["r0"]: q_pop_w += 1
            elif q_r1["r1"] < q_r1["r0"]: q_pop_l += 1
            else: q_pop_d += 1

    pop_n = len(c_pop_cash)
    print("\n" + "=" * 70)
    print("TASK 3: CAUSAL VALIDATION REPORT — POPULATION BENCHMARK")
    print("=" * 70)
    print(f"Matches per candidate: {pop_n} (4 opponents x 8 seeds x 2 seats)")
    print(f"V104 Control (2945):     {c_pop_w}W - {c_pop_l}L - {c_pop_d}D ({c_pop_w/pop_n*100:.1f}%)")
    print(f"V104 Quote Priority:     {q_pop_w}W - {q_pop_l}L - {q_pop_d}D ({q_pop_w/pop_n*100:.1f}%)")
    print("-" * 70)
    print(f"Final Cash Mean:     Quote=${np.mean(q_pop_cash):,.0f} | Ctrl=${np.mean(c_pop_cash):,.0f} | Delta=${np.mean(q_pop_cash)-np.mean(c_pop_cash):+,.0f}")
    print(f"Final Cash Median:   Quote=${np.median(q_pop_cash):,.0f} | Ctrl=${np.median(c_pop_cash):,.0f}")
    print(f"Final Cash Variance: Quote={np.var(q_pop_cash):,.0f} | Ctrl={np.var(c_pop_cash):,.0f}")
    print(f"Market Revenue Mean: Quote=${np.mean(q_pop_sales):,.0f} | Ctrl=${np.mean(c_pop_sales):,.0f} | Delta=${np.mean(q_pop_sales)-np.mean(c_pop_sales):+,.0f}")
    print(f"Premium Rev Mean:    Quote=${np.mean(q_pop_prem):,.0f} | Ctrl=${np.mean(c_pop_prem):,.0f} | Delta=${np.mean(q_pop_prem)-np.mean(c_pop_prem):+,.0f}")
    print("=" * 70)

    # Save summary to file
    summary_data = {
        "h2h": {
            "quote_wins": h2h_q_wins,
            "ctrl_wins": h2h_c_wins,
            "draws": h2h_draws,
            "quote_mean_cash": float(np.mean(q_cash_h2h)),
            "ctrl_mean_cash": float(np.mean(c_cash_h2h)),
            "delta_mean_cash": float(np.mean(q_cash_h2h) - np.mean(c_cash_h2h)),
            "quote_median_cash": float(np.median(q_cash_h2h)),
            "ctrl_median_cash": float(np.median(c_cash_h2h)),
            "quote_var_cash": float(np.var(q_cash_h2h)),
            "ctrl_var_cash": float(np.var(c_cash_h2h)),
            "quote_mean_sales": float(np.mean(q_sales_h2h)),
            "ctrl_mean_sales": float(np.mean(c_sales_h2h)),
            "quote_mean_prem": float(np.mean(q_prem_h2h)),
            "ctrl_mean_prem": float(np.mean(c_prem_h2h))
        },
        "population": {
            "quote_wins": q_pop_w,
            "quote_losses": q_pop_l,
            "quote_draws": q_pop_d,
            "ctrl_wins": c_pop_w,
            "ctrl_losses": c_pop_l,
            "ctrl_draws": c_pop_d,
            "quote_mean_cash": float(np.mean(q_pop_cash)),
            "ctrl_mean_cash": float(np.mean(c_pop_cash)),
            "delta_mean_cash": float(np.mean(q_pop_cash) - np.mean(c_pop_cash)),
            "quote_median_cash": float(np.median(q_pop_cash)),
            "ctrl_median_cash": float(np.median(c_pop_cash)),
            "quote_var_cash": float(np.var(q_pop_cash)),
            "ctrl_var_cash": float(np.var(c_pop_cash)),
            "quote_mean_sales": float(np.mean(q_pop_sales)),
            "ctrl_mean_sales": float(np.mean(c_pop_sales)),
            "quote_mean_prem": float(np.mean(q_pop_prem)),
            "ctrl_mean_prem": float(np.mean(c_pop_prem))
        }
    }
    with open(r"e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\causal_validation_v104.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print("Saved to RESEARCH/kaggle_loop/causal_validation_v104.json")

if __name__ == "__main__":
    main()
