import os
import sys
import time
import json
import numpy as np
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

def run_match(p0_path, p1_path, seed):
    agent0 = load_code(p0_path)
    agent1 = load_code(p1_path)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([agent0, agent1])

    PREMIUMS = {"STRAWBERRY", "MELON", "MILK", "WOOL"}
    p0_sales, p1_sales = 0.0, 0.0
    p0_prem, p1_prem = 0.0, 0.0

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
    v057 = r"e:\Setup\kaggle\kaggriculture\submission_v057_control.py"
    v16 = r"e:\Setup\kaggle\kaggriculture\agents\public_v16_rc5.py"

    h2h_seeds = [42, 101, 2024, 777, 9999, 123, 456, 789] # 16 games
    pop_seeds = [42, 101, 2024, 777] # 16 games (4 seeds x 2 seats x 2 opps)

    print("=" * 70, flush=True)
    print("SEQUENTIAL CAUSAL VALIDATION: V104 CONTROL VS V104 QUOTE PRIORITY", flush=True)
    print("=" * 70, flush=True)

    # 1. H2H: Quote vs Control
    print("\n--- Running H2H Matches (Quote Priority vs Control) ---", flush=True)
    h2h_q_cash, h2h_c_cash = [], []
    h2h_q_prem, h2h_c_prem = [], []
    h2h_q_sales, h2h_c_sales = [], []
    h2h_q_wins, h2h_c_wins, h2h_draws = 0, 0, 0

    t0 = time.time()
    for s in h2h_seeds:
        # Quote as P0, Control as P1
        res0 = run_match(quote, ctrl, s)
        h2h_q_cash.append(res0["r0"])
        h2h_c_cash.append(res0["r1"])
        h2h_q_prem.append(res0["p0_prem"])
        h2h_c_prem.append(res0["p1_prem"])
        h2h_q_sales.append(res0["p0_sales"])
        h2h_c_sales.append(res0["p1_sales"])
        if res0["r0"] > res0["r1"]: h2h_q_wins += 1
        elif res0["r1"] > res0["r0"]: h2h_c_wins += 1
        else: h2h_draws += 1
        print(f"Seed {s:5d} P0=Quote: Quote=${res0['r0']:,.0f} | Ctrl=${res0['r1']:,.0f} | Diff={res0['r0']-res0['r1']:+,.0f}", flush=True)

        # Control as P0, Quote as P1
        res1 = run_match(ctrl, quote, s)
        h2h_c_cash.append(res1["r0"])
        h2h_q_cash.append(res1["r1"])
        h2h_c_prem.append(res1["p0_prem"])
        h2h_q_prem.append(res1["p1_prem"])
        h2h_c_sales.append(res1["p0_sales"])
        h2h_q_sales.append(res1["p1_sales"])
        if res1["r1"] > res1["r0"]: h2h_q_wins += 1
        elif res1["r0"] > res1["r1"]: h2h_c_wins += 1
        else: h2h_draws += 1
        print(f"Seed {s:5d} P0=Ctrl : Quote=${res1['r1']:,.0f} | Ctrl=${res1['r0']:,.0f} | Diff={res1['r1']-res1['r0']:+,.0f}", flush=True)

    h2h_n = len(h2h_q_cash)
    print("-" * 70, flush=True)
    print(f"H2H Results ({h2h_n} games in {time.time()-t0:.1f}s):", flush=True)
    print(f"Quote Priority: {h2h_q_wins} W ({h2h_q_wins/h2h_n*100:.1f}%)", flush=True)
    print(f"Control (2945): {h2h_c_wins} W ({h2h_c_wins/h2h_n*100:.1f}%)", flush=True)
    print(f"Draws:          {h2h_draws} D ({h2h_draws/h2h_n*100:.1f}%)", flush=True)
    print(f"Mean Final Cash: Quote=${np.mean(h2h_q_cash):,.0f} | Ctrl=${np.mean(h2h_c_cash):,.0f} | Delta=${np.mean(h2h_q_cash)-np.mean(h2h_c_cash):+,.0f}", flush=True)
    print(f"Median Cash:     Quote=${np.median(h2h_q_cash):,.0f} | Ctrl=${np.median(h2h_c_cash):,.0f}", flush=True)
    print(f"Variance Cash:   Quote={np.var(h2h_q_cash):,.0f} | Ctrl={np.var(h2h_c_cash):,.0f}", flush=True)
    print(f"Mean Sales Rev:  Quote=${np.mean(h2h_q_sales):,.0f} | Ctrl=${np.mean(h2h_c_sales):,.0f} | Delta=${np.mean(h2h_q_sales)-np.mean(h2h_c_sales):+,.0f}", flush=True)
    print(f"Mean Prem Rev:   Quote=${np.mean(h2h_q_prem):,.0f} | Ctrl=${np.mean(h2h_c_prem):,.0f} | Delta=${np.mean(h2h_q_prem)-np.mean(h2h_c_prem):+,.0f}", flush=True)

    # 2. Candidate vs Opponents (V057 and V16)
    print("\n--- Running Population Matches (Control vs V057/V16, Quote vs V057/V16) ---", flush=True)
    ctrl_opp_w, ctrl_opp_l, ctrl_opp_d = 0, 0, 0
    quote_opp_w, quote_opp_l, quote_opp_d = 0, 0, 0
    ctrl_pop_cash, quote_pop_cash = [], []

    for opp_path in [v057, v16]:
        opp_name = os.path.basename(opp_path)
        for s in pop_seeds:
            # Control P0 & P1
            c0 = run_match(ctrl, opp_path, s)
            ctrl_pop_cash.append(c0["r0"])
            if c0["r0"] > c0["r1"]: ctrl_opp_w += 1
            elif c0["r0"] < c0["r1"]: ctrl_opp_l += 1
            else: ctrl_opp_d += 1

            c1 = run_match(opp_path, ctrl, s)
            ctrl_pop_cash.append(c1["r1"])
            if c1["r1"] > c1["r0"]: ctrl_opp_w += 1
            elif c1["r1"] < c1["r0"]: ctrl_opp_l += 1
            else: ctrl_opp_d += 1

            # Quote P0 & P1
            q0 = run_match(quote, opp_path, s)
            quote_pop_cash.append(q0["r0"])
            if q0["r0"] > q0["r1"]: quote_opp_w += 1
            elif q0["r0"] < q0["r1"]: quote_opp_l += 1
            else: quote_opp_d += 1

            q1 = run_match(opp_path, quote, s)
            quote_pop_cash.append(q1["r1"])
            if q1["r1"] > q1["r0"]: quote_opp_w += 1
            elif q1["r1"] < q1["r0"]: quote_opp_l += 1
            else: quote_opp_d += 1

            print(f"vs {opp_name:25} s={s:5d}: Ctrl=${(c0['r0']+c1['r1'])/2:,.0f} | Quote=${(q0['r0']+q1['r1'])/2:,.0f}", flush=True)

    pop_n = len(ctrl_pop_cash)
    print("-" * 70, flush=True)
    print(f"Population Benchmark Results ({pop_n} matches per agent):", flush=True)
    print(f"V104 Control (2945): {ctrl_opp_w}W - {ctrl_opp_l}L - {ctrl_opp_d}D ({ctrl_opp_w/pop_n*100:.1f}%) | Mean Cash: ${np.mean(ctrl_pop_cash):,.0f}", flush=True)
    print(f"V104 Quote Priority: {quote_opp_w}W - {quote_opp_l}L - {quote_opp_d}D ({quote_opp_w/pop_n*100:.1f}%) | Mean Cash: ${np.mean(quote_pop_cash):,.0f}", flush=True)
    print(f"Causal Delta (Quote - Control): Mean Cash: ${np.mean(quote_pop_cash)-np.mean(ctrl_pop_cash):+,.0f}", flush=True)
    print("=" * 70, flush=True)

    summary = {
        "h2h": {
            "n": h2h_n,
            "quote_wins": h2h_q_wins,
            "ctrl_wins": h2h_c_wins,
            "draws": h2h_draws,
            "quote_mean_cash": float(np.mean(h2h_q_cash)),
            "ctrl_mean_cash": float(np.mean(h2h_c_cash)),
            "delta_mean_cash": float(np.mean(h2h_q_cash) - np.mean(h2h_c_cash)),
            "quote_median_cash": float(np.median(h2h_q_cash)),
            "ctrl_median_cash": float(np.median(h2h_c_cash)),
            "quote_var_cash": float(np.var(h2h_q_cash)),
            "ctrl_var_cash": float(np.var(h2h_c_cash)),
            "quote_mean_sales": float(np.mean(h2h_q_sales)),
            "ctrl_mean_sales": float(np.mean(h2h_c_sales)),
            "quote_mean_prem": float(np.mean(h2h_q_prem)),
            "ctrl_mean_prem": float(np.mean(h2h_c_prem))
        },
        "population": {
            "n": pop_n,
            "quote_wins": quote_opp_w,
            "ctrl_wins": ctrl_opp_w,
            "quote_mean_cash": float(np.mean(quote_pop_cash)),
            "ctrl_mean_cash": float(np.mean(ctrl_pop_cash)),
            "delta_mean_cash": float(np.mean(quote_pop_cash) - np.mean(ctrl_pop_cash))
        }
    }
    with open(r"e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\causal_validation_v104.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved results to RESEARCH/kaggle_loop/causal_validation_v104.json", flush=True)

if __name__ == "__main__":
    main()
