"""
Step 2, 4, and 5: Verification & Regression Tests for V025-A Promotion
=====================================================================
"""

import hashlib
import time
import py_compile
import numpy as np
from kaggle_environments import make
import importlib.util

def get_file_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def test_syntax(filepath):
    py_compile.compile(filepath, doraise=True)
    return True

def run_smoke_test(agent_path, seed=42):
    spec = importlib.util.spec_from_file_location("mod_test", agent_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    agent = mod.agent

    t0 = time.time()
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
    env.run([agent, "random"])
    dt = time.time() - t0
    r0 = float(env.steps[-1][0]["reward"])
    r1 = float(env.steps[-1][1]["reward"])
    return r0, r1, dt

def run_regression_suite(agent_path):
    spec = importlib.util.spec_from_file_location("mod_reg", agent_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cand_agent = mod.agent

    spec_g = importlib.util.spec_from_file_location("mod_g", "agents/v023_g_capital_optimizer.py")
    mod_g = importlib.util.module_from_spec(spec_g)
    spec_g.loader.exec_module(mod_g)
    v23_agent = mod_g.agent

    # 1. Deterministic seeds vs Random
    random_seeds = [42, 100, 200, 500, 1000]
    random_results = {}
    for s in random_seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([cand_agent, "random"])
        r = float(env.steps[-1][0]["reward"])
        random_results[s] = r

    # 2. Paired seeds vs V023-G (20 seeds = 40 games)
    h2h_seeds = list(range(8000, 8020))
    cand_scores = []
    v23_scores = []
    wins = 0

    for s in h2h_seeds:
        # Game 1: Cand P0, V23 P1
        env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env0.run([cand_agent, v23_agent])
        r0 = float(env0.steps[-1][0]["reward"])
        opp0 = float(env0.steps[-1][1]["reward"])
        cand_scores.append(r0)
        v23_scores.append(opp0)
        if r0 > opp0: wins += 1

        # Game 2: V23 P0, Cand P1
        env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env1.run([v23_agent, cand_agent])
        opp1 = float(env1.steps[-1][0]["reward"])
        r1 = float(env1.steps[-1][1]["reward"])
        cand_scores.append(r1)
        v23_scores.append(opp1)
        if r1 > opp1: wins += 1

    return {
        "random_results": random_results,
        "cand_mean": float(np.mean(cand_scores)),
        "v23_mean": float(np.mean(v23_scores)),
        "delta": float(np.mean(cand_scores) - np.mean(v23_scores)),
        "win_rate": float((wins / len(cand_scores)) * 100.0),
        "total_games": len(cand_scores)
    }

if __name__ == "__main__":
    cand_path = "agents/v025_a_aggressive_cows.py"
    sha = get_file_sha256(cand_path)
    print(f"Candidate File: {cand_path}")
    print(f"SHA-256: {sha}")
    test_syntax(cand_path)
    print("Syntax check: PASSED")
    r0, r1, dt = run_smoke_test(cand_path, seed=42)
    print(f"Smoke Test (Seed 42 vs Random): Reward={r0:,.0f} vs {r1:,.0f} in {dt:.2f}s (PASSED)")
