"""
Fast Direct Head-to-Head Comparison: V025 Candidates vs V023-G
=============================================================
"""

import importlib.util
import numpy as np
import os
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location("mod_" + os.path.basename(path), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v23_g = load_agent("agents/v023_g_capital_optimizer.py")

candidates = [
    ("V025-A (Cows)", "agents/v025_a_aggressive_cows.py"),
    ("V025-B (Ramp)", "agents/v025_b_balanced_ramp.py"),
    ("V025-E (Hyb)",  "agents/v025_e_hybrid_flywheel.py"),
]

seeds = list(range(100, 125)) # 25 seeds = 50 games

print("=" * 105)
print(f"DIRECT HEAD-TO-HEAD VS V023-G CHAMPION (25 Seeds = 50 Games)")
print("=" * 105)

for cname, cpath in candidates:
    cand_agent = load_agent(cpath)
    c_scores = []
    g_scores = []
    wins, losses, ties = 0, 0, 0
    
    for s in seeds:
        # P0 game
        env0 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env0.run([cand_agent, v23_g])
        r0_c = float(env0.steps[-1][0]["reward"])
        r0_g = float(env0.steps[-1][1]["reward"])
        c_scores.append(r0_c)
        g_scores.append(r0_g)
        if r0_c > r0_g: wins += 1
        elif r0_c == r0_g: ties += 1
        else: losses += 1
        
        # P1 game
        env1 = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env1.run([v23_g, cand_agent])
        r1_g = float(env1.steps[-1][0]["reward"])
        r1_c = float(env1.steps[-1][1]["reward"])
        c_scores.append(r1_c)
        g_scores.append(r1_g)
        if r1_c > r1_g: wins += 1
        elif r1_c == r1_g: ties += 1
        else: losses += 1
        
    total = len(c_scores)
    wr = (wins / total) * 100.0
    cm = float(np.mean(c_scores))
    gm = float(np.mean(g_scores))
    delta = cm - gm
    cmed = float(np.median(c_scores))
    cmin = float(np.min(c_scores))
    cmax = float(np.max(c_scores))
    p10 = float(np.percentile(c_scores, 10))
    p25 = float(np.percentile(c_scores, 25))
    
    print(f"[{cname:<14} vs V023-G] WR: {wr:5.1f}% ({wins:2d}W/{losses:2d}L) | Cand Mean: ${cm:7,.0f} | V23 Mean: ${gm:7,.0f} | Delta: ${delta:+7,.0f} | Med: ${cmed:7,.0f} | P10: ${p10:7,.0f} | Min: ${cmin:7,.0f} | Max: ${cmax:7,.0f}", flush=True)
