import os
import json
import numpy as np
from kaggle_environments import make
import importlib.util

def load_agent(agent_file):
    spec = importlib.util.spec_from_file_location("agent_c", agent_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

AGENT_PATH = "agents/v018_c_inventory_pacing_v2.py"
SEEDS = [1, 2, 3, 4, 5]
THRESHOLDS = [30, 50, 75, 100]

print("=" * 50)
print("V018-C-v2 Threshold Sweep (T=30, 50, 75, 100)")
print("=" * 50)

all_results = {}

for t in THRESHOLDS:
    os.environ["V018_C_TARGET_PIPELINE"] = str(t)
    # Reload agent fresh for each threshold to reset global _METRICS
    agent_mod = load_agent(AGENT_PATH)

    banks = []
    rejections_list = []
    plants_list = []
    harvests_list = []
    deaths_list = []
    misses_list = []
    useful_list = []
    move_list = []
    idle_list = []
    pipeline_by_crop = {c: [] for c in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]}

    for seed in SEEDS:
        os.environ["KAGGRICULTURE_SEED"] = str(seed)
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})

        def make_wrapper(mod):
            def wrapper(obs):
                return mod.agent(obs)
            return wrapper

        steps = env.run([make_wrapper(agent_mod), "random"])
        bank = steps[-1][0].reward or 0
        banks.append(bank)

        # Read metrics from disk (written every 20 steps by the agent)
        mpath = f"experiments/metrics/game_{seed}_p0.json"
        m = {}
        if os.path.exists(mpath):
            with open(mpath) as f:
                m = json.load(f)

        crops = m.get("crops", {})
        workers = m.get("workers", {})
        farmer = m.get("farmer", {})

        plants_list.append(sum(c.get("planted", 0) for c in crops.values()))
        harvests_list.append(sum(c.get("harvested", 0) for c in crops.values()))
        deaths_list.append(sum(c.get("deaths", 0) for c in crops.values()))
        misses_list.append(m.get("water", {}).get("misses", 0))
        useful_list.append(workers.get("useful_actions", 0) + farmer.get("useful_actions", 0))
        move_list.append(workers.get("movement_actions", 0) + farmer.get("movement_actions", 0))
        idle_list.append(workers.get("idle_turns", 0) + farmer.get("idle_turns", 0))
        rejections_list.append(m.get("c1_rejections", 0))

        pv = m.get("pipeline_values", {})
        for crop in pipeline_by_crop:
            vals = pv.get(crop, [])
            if vals:
                pipeline_by_crop[crop].extend(vals)

    mean_bank = np.mean(banks)
    med_bank = np.median(banks)
    useful = np.mean(useful_list)
    moves = np.mean(move_list)
    move_eff = useful / max(1, useful + moves) * 100

    print(f"\nT={t}:")
    print(f"  Banks:          {[int(b) for b in banks]}")
    print(f"  Mean Bank:      ${mean_bank:,.2f}")
    print(f"  Median Bank:    ${med_bank:,.2f}")
    print(f"  Plants:         {np.mean(plants_list):.1f}")
    print(f"  Harvests:       {np.mean(harvests_list):.1f}")
    print(f"  Crop Deaths:    {np.mean(deaths_list):.1f}")
    print(f"  Water Misses:   {np.mean(misses_list):.1f}")
    print(f"  Useful Acts:    {useful:.1f}")
    print(f"  Move Acts:      {moves:.1f}")
    print(f"  Move Eff:       {move_eff:.1f}%")
    print(f"  Idle:           {np.mean(idle_list):.1f}")
    print(f"  C1 Rejections:  {np.mean(rejections_list):.1f}")
    print(f"  Pipeline means:")
    for crop, vals in pipeline_by_crop.items():
        if vals:
            print(f"    {crop}: mean={np.mean(vals):.1f} max={max(vals):.0f}")

    all_results[t] = {
        "mean_bank": mean_bank,
        "median_bank": med_bank,
        "banks": banks,
        "mean_plants": np.mean(plants_list),
        "mean_deaths": np.mean(deaths_list),
        "mean_misses": np.mean(misses_list),
        "mean_useful": useful,
        "mean_moves": moves,
        "move_eff": move_eff,
        "mean_idle": np.mean(idle_list),
        "mean_rejections": np.mean(rejections_list),
    }

print("\n" + "=" * 50)
print("SWEEP SUMMARY")
print("=" * 50)
print(f"{'T':>5} | {'Mean Bank':>12} | {'Med Bank':>10} | {'Plants':>7} | {'Deaths':>7} | {'Rejects':>8}")
print("-" * 60)
for t, r in all_results.items():
    print(f"{t:>5} | ${r['mean_bank']:>11,.2f} | ${r['median_bank']:>9,.2f} | {r['mean_plants']:>7.1f} | {r['mean_deaths']:>7.1f} | {r['mean_rejections']:>8.1f}")

best_t = max(all_results, key=lambda t: all_results[t]["mean_bank"])
print(f"\nBest threshold: T={best_t} with mean bank ${all_results[best_t]['mean_bank']:,.2f}")
