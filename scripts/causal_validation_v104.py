import os
import sys
import time
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

PREMIUM_GOODS = {"STRAWBERRY", "MELON", "MILK", "WOOL"}

def _run_detailed_match(args):
    p0_path, p1_path, seed, label = args
    
    # Suppress C++ OpenSpiel import spam via OS-level FD redirection
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

    def load_code(p):
        ns = {}
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, os.path.basename(p), "exec"), ns)
        callables = [v for v in ns.values() if callable(v)]
        if not callables:
            raise ValueError(f"No callable found in {p}")
        return callables[-1]

    agent0 = load_code(p0_path)
    agent1 = load_code(p1_path)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([agent0, agent1])

    # Extract match telemetry
    # Parse steps to calculate market revenue and premium revenue for each player
    # Each step has step[i]['action'] and step[i]['observation']
    # But market processing updates money. Let's trace money deltas or action executions.
    # More reliably: trace sell actions that actually occurred.
    # In kaggriculture: obs.market.prices gives price at start of turn.
    
    p0_sales_rev = 0.0
    p1_sales_rev = 0.0
    p0_premium_rev = 0.0
    p1_premium_rev = 0.0

    steps = env.steps
    for s_idx in range(len(steps) - 1):
        step_now = steps[s_idx]
        step_next = steps[s_idx + 1]
        
        # obs of step_now
        obs0 = step_now[0]["observation"]
        prices = obs0.get("market", {}).get("prices", {})
        
        # money delta
        m0_before = step_now[0]["observation"]["farms"][0]["money"]
        m0_after = step_next[0]["observation"]["farms"][0]["money"]
        m1_before = step_now[1]["observation"]["farms"][1]["money"]
        m1_after = step_next[1]["observation"]["farms"][1]["money"]

        # Player 0 action
        act0 = step_now[0].get("action") or {}
        if isinstance(act0, dict):
            for order in act0.get("market", []):
                if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
                    item, qty = order[1], order[2]
                    p = prices.get(item, 1)
                    val = p * qty
                    p0_sales_rev += val
                    if item in PREMIUM_GOODS:
                        p0_premium_rev += val

        # Player 1 action
        act1 = step_now[1].get("action") or {}
        if isinstance(act1, dict):
            for order in act1.get("market", []):
                if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
                    item, qty = order[1], order[2]
                    p = prices.get(item, 1)
                    val = p * qty
                    p1_sales_rev += val
                    if item in PREMIUM_GOODS:
                        p1_premium_rev += val

    final = env.steps[-1]
    r0 = float(final[0].get("reward", 0) or 0)
    r1 = float(final[1].get("reward", 0) or 0)
    s0 = final[0].get("status", "UNKNOWN")
    s1 = final[1].get("status", "UNKNOWN")

    return {
        "p0_path": os.path.basename(p0_path),
        "p1_path": os.path.basename(p1_path),
        "seed": seed,
        "label": label,
        "r0": r0,
        "r1": r1,
        "s0": s0,
        "s1": s1,
        "p0_sales_rev": p0_sales_rev,
        "p1_sales_rev": p1_sales_rev,
        "p0_premium_rev": p0_premium_rev,
        "p1_premium_rev": p1_premium_rev,
    }

def run_causal_study(max_workers=6):
    v104_control = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    v104_quote = r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py"
    
    pop = [
        r"e:\Setup\kaggle\kaggriculture\submission_v057_control.py",
        r"e:\Setup\kaggle\kaggriculture\agents\public_v16_rc5.py",
        r"e:\Setup\kaggle\kaggriculture\agents\013_robust_trace.py",
        r"e:\Setup\kaggle\kaggriculture\agents\v081_kaggle_83k_trace.py"
    ]

    h2h_seeds = [42, 101, 2024, 777, 9999, 123, 456, 789, 2025, 99999,
                 11, 22, 33, 44, 55, 66, 77, 88, 99, 111,
                 222, 333, 444, 555, 666, 7777, 8888, 1234, 5678, 9012, 31415, 27182]
    
    pop_seeds = [42, 101, 2024, 777, 9999, 123, 456, 789, 2025, 99999,
                 11, 22, 33, 44, 55, 66]

    tasks = []

    # 1. H2H tasks: Control vs Quote
    for s in h2h_seeds:
        # Quote as P0, Control as P1
        tasks.append((v104_quote, v104_control, s, "H2H_QuoteP0"))
        # Control as P0, Quote as P1
        tasks.append((v104_control, v104_quote, s, "H2H_ControlP0"))

    # 2. Control vs Population & Quote vs Population (Identical conditions)
    for opp in pop:
        for s in pop_seeds:
            # Control as P0 & P1
            tasks.append((v104_control, opp, s, f"Control_vs_{os.path.basename(opp)}_P0"))
            tasks.append((opp, v104_control, s, f"Control_vs_{os.path.basename(opp)}_P1"))
            # Quote as P0 & P1
            tasks.append((v104_quote, opp, s, f"Quote_vs_{os.path.basename(opp)}_P0"))
            tasks.append((opp, v104_quote, s, f"Quote_vs_{os.path.basename(opp)}_P1"))

    print(f"Total Causal Validation Matches: {len(tasks)} across {max_workers} workers...")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_run_detailed_match, t): t for t in tasks}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            results.append(res)
            completed += 1
            if completed % 25 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} matches ({time.time()-t0:.1f}s)...")

    # Analyze H2H: Quote vs Control
    h2h_quote_wins = 0
    h2h_ctrl_wins = 0
    h2h_draws = 0
    quote_cash_list = []
    ctrl_cash_list = []
    quote_prem_list = []
    ctrl_prem_list = []
    quote_sales_list = []
    ctrl_sales_list = []

    for r in results:
        if r["label"] == "H2H_QuoteP0":
            q_cash, c_cash = r["r0"], r["r1"]
            q_prem, c_prem = r["p0_premium_rev"], r["p1_premium_rev"]
            q_sales, c_sales = r["p0_sales_rev"], r["p1_sales_rev"]
            quote_cash_list.append(q_cash)
            ctrl_cash_list.append(c_cash)
            quote_prem_list.append(q_prem)
            ctrl_prem_list.append(c_prem)
            quote_sales_list.append(q_sales)
            ctrl_sales_list.append(c_sales)
            if q_cash > c_cash: h2h_quote_wins += 1
            elif c_cash > q_cash: h2h_ctrl_wins += 1
            else: h2h_draws += 1
        elif r["label"] == "H2H_ControlP0":
            c_cash, q_cash = r["r0"], r["r1"]
            c_prem, q_prem = r["p0_premium_rev"], r["p1_premium_rev"]
            c_sales, q_sales = r["p0_sales_rev"], r["p1_sales_rev"]
            quote_cash_list.append(q_cash)
            ctrl_cash_list.append(c_cash)
            quote_prem_list.append(q_prem)
            ctrl_prem_list.append(c_prem)
            quote_sales_list.append(q_sales)
            ctrl_sales_list.append(c_sales)
            if q_cash > c_cash: h2h_quote_wins += 1
            elif c_cash > q_cash: h2h_ctrl_wins += 1
            else: h2h_draws += 1

    h2h_total = h2h_quote_wins + h2h_ctrl_wins + h2h_draws
    print("\n" + "=" * 70)
    print(f"HEAD-TO-HEAD: V104 Quote Priority vs V104 Control (2945 Base)")
    print(f"Matches: {h2h_total} (32 paired seeds, both seats)")
    print(f"Quote Priority: {h2h_quote_wins} W ({h2h_quote_wins/h2h_total*100:.1f}%)")
    print(f"Control (2945): {h2h_ctrl_wins} W ({h2h_ctrl_wins/h2h_total*100:.1f}%)")
    print(f"Draws:          {h2h_draws} D ({h2h_draws/h2h_total*100:.1f}%)")
    print("-" * 70)
    print(f"Mean Final Cash:   Quote=${np.mean(quote_cash_list):,.0f} | Ctrl=${np.mean(ctrl_cash_list):,.0f} (Diff: ${np.mean(quote_cash_list)-np.mean(ctrl_cash_list):+,.0f})")
    print(f"Median Final Cash: Quote=${np.median(quote_cash_list):,.0f} | Ctrl=${np.median(ctrl_cash_list):,.0f}")
    print(f"StdDev Cash:       Quote=${np.std(quote_cash_list):,.0f} | Ctrl=${np.std(ctrl_cash_list):,.0f}")
    print(f"Mean Premium Rev:  Quote=${np.mean(quote_prem_list):,.0f} | Ctrl=${np.mean(ctrl_prem_list):,.0f} (Diff: ${np.mean(quote_prem_list)-np.mean(ctrl_prem_list):+,.0f})")
    print(f"Mean Market Rev:   Quote=${np.mean(quote_sales_list):,.0f} | Ctrl=${np.mean(ctrl_sales_list):,.0f} (Diff: ${np.mean(quote_sales_list)-np.mean(ctrl_sales_list):+,.0f})")
    print("=" * 70)

    # Analyze vs Population (Paired per seed/seat/opponent)
    pop_ctrl_wins, pop_ctrl_losses, pop_ctrl_draws = 0, 0, 0
    pop_quote_wins, pop_quote_losses, pop_quote_draws = 0, 0, 0
    pop_ctrl_cash, pop_quote_cash = [], []
    pop_ctrl_prem, pop_quote_prem = [], []

    for opp in pop:
        opp_name = os.path.basename(opp)
        for s in pop_seeds:
            # P0 matches
            c_r0 = [r for r in results if r["label"] == f"Control_vs_{opp_name}_P0" and r["seed"] == s][0]
            q_r0 = [r for r in results if r["label"] == f"Quote_vs_{opp_name}_P0" and r["seed"] == s][0]
            
            c_cash, c_opp = c_r0["r0"], c_r0["r1"]
            q_cash, q_opp = q_r0["r0"], q_r0["r1"]
            
            pop_ctrl_cash.append(c_cash)
            pop_quote_cash.append(q_cash)
            pop_ctrl_prem.append(c_r0["p0_premium_rev"])
            pop_quote_prem.append(q_r0["p0_premium_rev"])

            if c_cash > c_opp: pop_ctrl_wins += 1
            elif c_cash < c_opp: pop_ctrl_losses += 1
            else: pop_ctrl_draws += 1

            if q_cash > q_opp: pop_quote_wins += 1
            elif q_cash < q_opp: pop_quote_losses += 1
            else: pop_quote_draws += 1

            # P1 matches
            c_r1 = [r for r in results if r["label"] == f"Control_vs_{opp_name}_P1" and r["seed"] == s][0]
            q_r1 = [r for r in results if r["label"] == f"Quote_vs_{opp_name}_P1" and r["seed"] == s][0]

            c_cash, c_opp = c_r1["r1"], c_r1["r0"]
            q_cash, q_opp = q_r1["r1"], q_r1["r0"]

            pop_ctrl_cash.append(c_cash)
            pop_quote_cash.append(q_cash)
            pop_ctrl_prem.append(c_r1["p1_premium_rev"])
            pop_quote_prem.append(q_r1["p1_premium_rev"])

            if c_cash > c_opp: pop_ctrl_wins += 1
            elif c_cash < c_opp: pop_ctrl_losses += 1
            else: pop_ctrl_draws += 1

            if q_cash > q_opp: pop_quote_wins += 1
            elif q_cash < q_opp: pop_quote_losses += 1
            else: pop_quote_draws += 1

    pop_total = pop_ctrl_wins + pop_ctrl_losses + pop_ctrl_draws
    print("\n" + "=" * 70)
    print(f"POPULATION BENCHMARK: Control vs Quote Priority (Identical Paired Setup)")
    print(f"Matches per candidate: {pop_total} (4 opponents x 16 seeds x 2 seats)")
    print("-" * 70)
    print(f"V104 Control (2945):     {pop_ctrl_wins:2d}W - {pop_ctrl_losses:2d}L - {pop_ctrl_draws:2d}D ({pop_ctrl_wins/pop_total*100:.1f}%) | Mean Cash: ${np.mean(pop_ctrl_cash):,.0f} | Median: ${np.median(pop_ctrl_cash):,.0f} | Std: ${np.std(pop_ctrl_cash):,.0f}")
    print(f"V104 Quote Priority:     {pop_quote_wins:2d}W - {pop_quote_losses:2d}L - {pop_quote_draws:2d}D ({pop_quote_wins/pop_total*100:.1f}%) | Mean Cash: ${np.mean(pop_quote_cash):,.0f} | Median: ${np.median(pop_quote_cash):,.0f} | Std: ${np.std(pop_quote_cash):,.0f}")
    print(f"Causal Delta (Quote-Ctrl): Mean Cash: ${np.mean(pop_quote_cash)-np.mean(pop_ctrl_cash):+,.0f} | Premium Rev: ${np.mean(pop_quote_prem)-np.mean(pop_ctrl_prem):+,.0f}")
    print("=" * 70)

    # Save detailed telemetry to json
    report_data = {
        "h2h": {
            "quote_wins": h2h_quote_wins,
            "ctrl_wins": h2h_ctrl_wins,
            "draws": h2h_draws,
            "quote_mean_cash": float(np.mean(quote_cash_list)),
            "ctrl_mean_cash": float(np.mean(ctrl_cash_list)),
            "quote_median_cash": float(np.median(quote_cash_list)),
            "ctrl_median_cash": float(np.median(ctrl_cash_list)),
            "quote_std_cash": float(np.std(quote_cash_list)),
            "ctrl_std_cash": float(np.std(ctrl_cash_list)),
            "quote_mean_prem": float(np.mean(quote_prem_list)),
            "ctrl_mean_prem": float(np.mean(ctrl_prem_list)),
            "quote_mean_sales": float(np.mean(quote_sales_list)),
            "ctrl_mean_sales": float(np.mean(ctrl_sales_list)),
        },
        "pop": {
            "ctrl_wins": pop_ctrl_wins,
            "ctrl_losses": pop_ctrl_losses,
            "ctrl_draws": pop_ctrl_draws,
            "quote_wins": pop_quote_wins,
            "quote_losses": pop_quote_losses,
            "quote_draws": pop_quote_draws,
            "ctrl_mean_cash": float(np.mean(pop_ctrl_cash)),
            "quote_mean_cash": float(np.mean(pop_quote_cash)),
            "ctrl_median_cash": float(np.median(pop_ctrl_cash)),
            "quote_median_cash": float(np.median(pop_quote_cash)),
            "ctrl_std_cash": float(np.std(pop_ctrl_cash)),
            "quote_std_cash": float(np.std(pop_quote_cash)),
            "ctrl_mean_prem": float(np.mean(pop_ctrl_prem)),
            "quote_mean_prem": float(np.mean(pop_quote_prem)),
        }
    }
    with open(r"e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\causal_validation_v104.json", "w") as f:
        json.dump(report_data, f, indent=2)
    print("Saved detailed report to RESEARCH/kaggle_loop/causal_validation_v104.json")

if __name__ == "__main__":
    run_causal_study(max_workers=6)
