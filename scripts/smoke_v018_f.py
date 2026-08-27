"""
Comparative smoke test: V018-B vs V018-D vs V018-F
- 5 identical seeds each agent
- Opponents: random + starter (10 games per agent total)
- Tracks all metrics including fallback activations
"""
import os
import sys
import json
import numpy as np
import importlib.util
from kaggle_environments import make

SEEDS = [1, 2, 3, 4, 5]
AGENTS = {
    "V018-B": "agents/v018_b_batch_cap.py",
    "V018-D": "agents/v018_d_subsistence.py",
    "V018-F": "agents/v018_f_subsistence_fixed.py",
}
OPPONENTS = ["random", "starter"]

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_game(agent_mod, opp, seed, env_vars=None):
    os.environ["KAGGRICULTURE_SEED"] = str(seed)
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = str(v)

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)

    def wrapper(obs):
        try:
            return agent_mod.agent(obs)
        except Exception as e:
            import traceback; traceback.print_exc()
            return {"farmer": ["PASS"], "hands": [], "market": []}

    env.run([wrapper, opp])
    final = env.steps[-1]
    reward = final[0].reward or 0

    metrics_path = f"experiments/metrics/game_{seed}_p0.json"
    m = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            m = json.load(f)

    return reward, m


def extract(m):
    econ = m.get("economy", {})
    farmer = m.get("farmer", {})
    workers = m.get("workers", {})
    water = m.get("water", {})
    crops = m.get("crops", {})
    v018 = m.get("v018", {})

    total_plants = sum(c.get("planted", 0) for c in crops.values())
    total_harvests = sum(c.get("harvested", 0) for c in crops.values())
    total_deaths = sum(c.get("deaths", 0) for c in crops.values())

    staple_plants = (crops.get("WHEAT", {}).get("planted", 0) +
                     crops.get("CARROT", {}).get("planted", 0))
    premium_plants = (crops.get("TOMATO", {}).get("planted", 0) +
                      crops.get("STRAWBERRY", {}).get("planted", 0) +
                      crops.get("MELON", {}).get("planted", 0))

    useful = (farmer.get("useful_actions", 0) + workers.get("useful_actions", 0))
    movement = (farmer.get("movement_actions", 0) + workers.get("movement_actions", 0))
    idle = (farmer.get("idle_turns", 0) + workers.get("idle_turns", 0))
    move_eff = useful / max(1, movement + useful)

    return {
        "bank": econ.get("final_money", 0),
        "revenue": econ.get("total_revenue", 0),
        "seed_spend": econ.get("seed_spending", 0),
        "land_spend": econ.get("land_spending", 0),
        "useful": useful,
        "movement": movement,
        "idle": idle,
        "move_eff": move_eff,
        "plants": total_plants,
        "harvests": total_harvests,
        "deaths": total_deaths,
        "watering_misses": water.get("misses", 0),
        "staple_plants": staple_plants,
        "premium_plants": premium_plants,
        "blocked_planting": v018.get("blocked_planting_quantity", 0),
        "empty_tile_days": v018.get("empty_tile_days", 0),
    }


all_results = {}  # agent_name -> list of metric dicts

for agent_name, agent_path in AGENTS.items():
    print(f"\n{'='*50}")
    print(f"Running {agent_name} ({agent_path})")
    print(f"{'='*50}")
    env_vars = {}
    if agent_name == "V018-D":
        env_vars = {"V018_D_EMPTY_LAND_TRIGGER": "10", "V018_D_FALLBACK_MODE": "WHEAT_ONLY"}
    elif agent_name == "V018-F":
        env_vars = {"V018_F_FALLBACK_TRIGGER": "10", "V018_B_CAP": "4"}

    agent_mod = load_agent(agent_path)
    results = []

    for opp in OPPONENTS:
        for seed in SEEDS:
            print(f"  {agent_name} vs {opp} seed={seed}", end=" ")
            reward, m = run_game(agent_mod, opp, seed, env_vars)
            if m:
                rec = extract(m)
                rec["seed"] = seed
                rec["opponent"] = opp
                results.append(rec)
                print(f"-> bank=${rec['bank']:.0f}")
            else:
                print("-> no metrics")

    all_results[agent_name] = results


# ── Summary Table ──────────────────────────────────────────────────────────
def mean(lst, key):
    vals = [r[key] for r in lst if key in r]
    return np.mean(vals) if vals else 0.0

METRICS = [
    ("bank", "Final Bank"),
    ("revenue", "Total Revenue"),
    ("seed_spend", "Seed Spend"),
    ("land_spend", "Land Spend"),
    ("useful", "Useful Actions"),
    ("movement", "Movement Actions"),
    ("idle", "Idle Turns"),
    ("move_eff", "Movement Efficiency"),
    ("plants", "Total Plants"),
    ("harvests", "Total Harvests"),
    ("deaths", "Crop Deaths"),
    ("watering_misses", "Water Misses"),
    ("staple_plants", "Staple Plants (W+C)"),
    ("premium_plants", "Premium Plants"),
    ("blocked_planting", "Blocked Plantings"),
    ("empty_tile_days", "Empty Tile-Days"),
]

print("\n\n" + "="*70)
print("COMPARATIVE SMOKE RESULTS (5 seeds × 2 opponents = 10 games each)")
print("="*70)

header = f"{'Metric':<30}" + "".join(f"{n:>14}" for n in AGENTS.keys())
print(header)
print("-" * (30 + 14 * len(AGENTS)))

for key, label in METRICS:
    row = f"{label:<30}"
    for agent_name in AGENTS.keys():
        v = mean(all_results[agent_name], key)
        if key in ("bank", "revenue", "seed_spend", "land_spend"):
            row += f"{'${:.0f}'.format(v):>14}"
        elif key == "move_eff":
            row += f"{'{:.1%}'.format(v):>14}"
        else:
            row += f"{'{:.1f}'.format(v):>14}"
    print(row)

# Per-opponent breakdown
print("\n\n" + "="*70)
print("PER-OPPONENT BREAKDOWN (Mean Final Bank)")
print("="*70)
header2 = f"{'Opponent':<14}" + "".join(f"{n:>14}" for n in AGENTS.keys())
print(header2)
print("-" * (14 + 14 * len(AGENTS)))
for opp in OPPONENTS:
    row = f"{opp:<14}"
    for agent_name in AGENTS.keys():
        subset = [r for r in all_results[agent_name] if r["opponent"] == opp]
        v = mean(subset, "bank")
        row += f"{'${:.0f}'.format(v):>14}"
    print(row)

# Staple vs premium breakdown
print("\n\n" + "="*70)
print("CROP MIX ANALYSIS")
print("="*70)
for agent_name, results in all_results.items():
    total_p = mean(results, "premium_plants")
    total_s = mean(results, "staple_plants")
    total = total_p + total_s
    pct_p = 100 * total_p / max(1, total)
    pct_s = 100 * total_s / max(1, total)
    print(f"{agent_name}: premium={total_p:.1f} ({pct_p:.0f}%), staple={total_s:.1f} ({pct_s:.0f}%)")

print("\nDone.")
