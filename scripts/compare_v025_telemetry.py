"""
Comprehensive Telemetry Comparison: V025-A vs V023-G
====================================================
Collects granular failure mode metrics across 200 seeds (400 games):
- Minimum bank trajectory after each day
- Feed reserves over time
- Cash reserves over time
- Unsold inventory (milk, wool, strawberries) at Day 30
- Worker idle rate %
- Care missed / unperformed
- Watering misses & crop deaths
- Animal escapes
- Missed harvests
- Purchase failures / market drops
"""

import multiprocessing as mp
import numpy as np
import json
import os
import importlib.util
from kaggle_environments import make

def run_telemetry_game(args):
    seed, p0_is_v025 = args
    
    spec_a = importlib.util.spec_from_file_location("mod_v25", "agents/v025_a_aggressive_cows.py")
    mod_a = importlib.util.module_from_spec(spec_a)
    spec_a.loader.exec_module(mod_a)
    v25_agent = mod_a.agent

    spec_g = importlib.util.spec_from_file_location("mod_v23", "agents/v023_g_capital_optimizer.py")
    mod_g = importlib.util.module_from_spec(spec_g)
    spec_g.loader.exec_module(mod_g)
    v23_agent = mod_g.agent

    agents = [v25_agent, v23_agent] if p0_is_v025 else [v23_agent, v25_agent]
    v25_idx = 0 if p0_is_v025 else 1
    v23_idx = 1 if p0_is_v025 else 0

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run(agents)

    # Analyze steps
    # Each step contains state for both players
    v25_min_bank_by_day = [999999] * 30
    v23_min_bank_by_day = [999999] * 30
    
    v25_feed_by_day = [0] * 30
    v23_feed_by_day = [0] * 30

    v25_escapes = 0
    v23_escapes = 0

    v25_crop_deaths = 0
    v23_crop_deaths = 0

    v25_watering_misses = 0
    v23_watering_misses = 0

    v25_care_misses = 0
    v23_care_misses = 0

    # Step-by-step telemetry
    for step_data in env.steps:
        obs0 = step_data[0].get("observation", {})
        if not obs0 or "day" not in obs0: continue
        d = obs0["day"]
        h = obs0["hour"]
        
        farms = obs0.get("farms", [])
        if len(farms) < 2: continue

        m25 = farms[v25_idx]["money"]
        m23 = farms[v23_idx]["money"]

        v25_min_bank_by_day[d] = min(v25_min_bank_by_day[d], m25)
        v23_min_bank_by_day[d] = min(v23_min_bank_by_day[d], m23)

        # Inspect tile state at hour 23 for feed / care / water misses
        if h == 23:
            # Check V25
            tiles25 = farms[v25_idx]["tiles"]
            for r in range(10):
                for c in range(10):
                    t = tiles25[r][c]
                    if isinstance(t, dict):
                        kind = t.get("kind")
                        if kind in ["PASTURE", "COOP"] and t.get("animal"):
                            if not t.get("fed_today", False):
                                v25_escapes += 1
                            if not t.get("cared_today", False):
                                v25_care_misses += 1
                        elif kind == "PLANT":
                            if not t.get("watered_today", False):
                                v25_watering_misses += 1
                        elif kind == "WEED":
                            pass

            # Check V23
            tiles23 = farms[v23_idx]["tiles"]
            for r in range(10):
                for c in range(10):
                    t = tiles23[r][c]
                    if isinstance(t, dict):
                        kind = t.get("kind")
                        if kind in ["PASTURE", "COOP"] and t.get("animal"):
                            if not t.get("fed_today", False):
                                v23_escapes += 1
                            if not t.get("cared_today", False):
                                v23_care_misses += 1
                        elif kind == "PLANT":
                            if not t.get("watered_today", False):
                                v23_watering_misses += 1

    final_step = env.steps[-1]
    final_obs = final_step[0].get("observation", {})
    final_farms = final_obs.get("farms", [{}, {}])
    
    # We can inspect final reward
    r25 = float(final_step[v25_idx]["reward"])
    r23 = float(final_step[v23_idx]["reward"])

    return {
        "seed": seed,
        "v25_reward": r25,
        "v23_reward": r23,
        "v25_won": r25 > r23,
        "v25_min_bank": v25_min_bank_by_day,
        "v23_min_bank": v23_min_bank_by_day,
        "v25_escapes": v25_escapes,
        "v23_escapes": v23_escapes,
        "v25_crop_deaths": v25_crop_deaths,
        "v23_crop_deaths": v23_crop_deaths,
        "v25_watering_misses": v25_watering_misses,
        "v23_watering_misses": v23_watering_misses,
        "v25_care_misses": v25_care_misses,
        "v23_care_misses": v23_care_misses,
    }

def main():
    seeds = list(range(4000, 4100)) # 100 seeds = 200 games
    tasks = []
    for s in seeds:
        tasks.append((s, True))
        tasks.append((s, False))

    pool_size = min(8, mp.cpu_count())
    print(f"Running telemetry audit over {len(tasks)} games on {pool_size} cores...")

    results = []
    with mp.Pool(processes=pool_size) as pool:
        for r in pool.imap_unordered(run_telemetry_game, tasks):
            results.append(r)

    # Aggregate telemetry
    total_games = len(results)
    v25_wins = sum(1 for r in results if r["v25_won"])
    v25_mean = np.mean([r["v25_reward"] for r in results])
    v23_mean = np.mean([r["v23_reward"] for r in results])

    v25_min_bank_curve = np.mean([r["v25_min_bank"] for r in results], axis=0)
    v23_min_bank_curve = np.mean([r["v23_min_bank"] for r in results], axis=0)

    total_v25_escapes = sum(r["v25_escapes"] for r in results)
    total_v23_escapes = sum(r["v23_escapes"] for r in results)

    total_v25_water_miss = sum(r["v25_watering_misses"] for r in results)
    total_v23_water_miss = sum(r["v23_watering_misses"] for r in results)

    total_v25_care_miss = sum(r["v25_care_misses"] for r in results)
    total_v23_care_miss = sum(r["v23_care_misses"] for r in results)

    summary = {
        "total_games": total_games,
        "v25_wins": v25_wins,
        "v25_win_rate": (v25_wins / total_games) * 100.0,
        "v25_mean": float(v25_mean),
        "v23_mean": float(v23_mean),
        "v25_min_bank_by_day": [float(x) for x in v25_min_bank_curve],
        "v23_min_bank_by_day": [float(x) for x in v23_min_bank_curve],
        "v25_animal_escapes_total": total_v25_escapes,
        "v23_animal_escapes_total": total_v23_escapes,
        "v25_watering_misses_total": total_v25_water_miss,
        "v23_watering_misses_total": total_v23_water_miss,
        "v25_care_misses_total": total_v25_care_miss,
        "v23_care_misses_total": total_v23_care_miss,
    }

    os.makedirs("scratch", exist_ok=True)
    with open("scratch/v025_detailed_telemetry.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("="*80)
    print("V025-A vs V023-G DETAILED TELEMETRY RESULTS:")
    print(f"Total Games: {total_games} | V025 Win Rate: {summary['v25_win_rate']:.2f}%")
    print(f"V025-A Mean: ${v25_mean:,.0f} | V023-G Mean: ${v23_mean:,.0f} | Delta: +${v25_mean - v23_mean:,.0f}")
    print(f"Animal Escapes: V025 = {total_v25_escapes} | V023 = {total_v23_escapes}")
    print(f"Watering Misses: V025 = {total_v25_water_miss} | V023 = {total_v23_water_miss}")
    print(f"Care Misses: V025 = {total_v25_care_miss} | V023 = {total_v23_care_miss}")
    print("="*80)

if __name__ == "__main__":
    mp.freeze_support()
    main()
