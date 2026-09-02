"""
Ablation Benchmark Runner (Ablations A, B, C, D vs V020-C)
"""
import importlib.util
import numpy as np
import json
from kaggle_environments import make

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

v020_c = load_agent("agents/v020_c_competitive_surgical.py")
v022_c = load_agent("agents/v022_c_market_batching.py")
abl_a = load_agent("agents/ablations/v022_minus_a_crop_open.py")
abl_b = load_agent("agents/ablations/v022_minus_b_dump_sell.py")
abl_c = load_agent("agents/ablations/v022_minus_c_low_labor.py")
abl_d = load_agent("agents/ablations/v022_minus_d_dispersed_pastures.py")

ABLATIONS = [
    ("Full V022-C Control", v022_c),
    ("V022-C-minus-A (Crop Open)", abl_a),
    ("V022-C-minus-B (Bulk Dump Sell)", abl_b),
    ("V022-C-minus-C (Static Low Labor 3)", abl_c),
    ("V022-C-minus-D (Dispersed Pastures)", abl_d),
]

SEEDS = list(range(840, 850)) # 10 fresh seeds * 2 positions = 20 games each

ablation_results = {}

print("="*80)
print("RUNNING FACTORIAL ABLATION SUITE (20 GAMES EACH VS V020-C)")
print("="*80)

for name, ag in ABLATIONS:
    scores = []
    opp_scores = []
    wins = 0
    losses = 0
    ties = 0
    
    for s in SEEDS:
        # P0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([ag, v020_c])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        scores.append(r0)
        opp_scores.append(r1)
        if r0 > r1: wins += 1
        elif r0 == r1: ties += 1
        else: losses += 1
        
        # P1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.run([v020_c, ag])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        scores.append(r1)
        opp_scores.append(r0)
        if r1 > r0: wins += 1
        elif r1 == r0: ties += 1
        else: losses += 1
        
    wr = (wins / len(scores)) * 100.0
    c_m = np.mean(scores)
    o_m = np.mean(opp_scores)
    print(f"{name:<38}: Win Rate: {wr:5.1f}% ({wins:2d}W/{losses:2d}L/{ties:1d}T) | Mean: ${c_m:7,.0f} | Opp Mean: ${o_m:7,.0f} | Delta: ${c_m-o_m:+7,.0f}")
    ablation_results[name] = {
        "win_rate": wr,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "mean_score": float(c_m),
        "opp_mean_score": float(o_m),
        "delta": float(c_m - o_m)
    }

with open("scratch/ablation_results.json", "w") as f:
    json.dump(ablation_results, f, indent=2)

print("\nAblation benchmarks completed and saved to scratch/ablation_results.json")
