import os
import sys
import json
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from kaggle_environments import make

import importlib.util

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location("agent_module", filepath)
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

def run_game(args):
    agent_path, opp_path, seed, p1_is_agent = args
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    os.environ["KAGGRICULTURE_SEED"] = str(seed)
    
    agent1 = load_agent(agent_path)
    agent2 = load_agent(opp_path)
    
    agents = [agent1, agent2] if p1_is_agent else [agent2, agent1]
    
    try:
        env.run(agents)
        final = env.steps[-1]
        
        metric_file = f"experiments/metrics/game_{seed}_p{0 if p1_is_agent else 1}.json"
        metrics = {}
        if os.path.exists(metric_file):
            with open(metric_file, "r") as f:
                metrics = json.load(f)
                
        r_a1 = final[0].reward if p1_is_agent else final[1].reward
        return {"status": "SUCCESS", "reward": r_a1 or 0, "metrics": metrics, "seed": seed}
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "reward": 0, "seed": seed}

def run_sweep(name, agent_path, configs, num_seeds=10):
    opponents = ["random", "pass", "starter"]
    results = {}
    
    for conf_name, env_vars in configs.items():
        print(f"Sweeping {name} - {conf_name}...")
        for k, v in env_vars.items():
            os.environ[k] = str(v)
            
        tasks = []
        for opp in opponents:
            for i in range(num_seeds):
                seed = 42 + i
                p1_is_agent = (i % 2 == 0)
                tasks.append((agent_path, opp, seed, p1_is_agent))
                
        rewards = []
        for t in tasks:
            res = run_game(t)
            if res["status"] == "SUCCESS":
                rewards.append(res["reward"])
                
        mean_reward = np.mean(rewards) if rewards else 0
        results[conf_name] = mean_reward
        print(f"  Mean Reward: ${mean_reward:.2f}")
        
    best_config = max(results, key=results.get)
    print(f"Best for {name}: {best_config} with ${results[best_config]:.2f}")
    return best_config, configs[best_config]

def analyze_benchmark(agent_path, opps, num_seeds, env_vars=None):
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = str(v)
            
    tasks = []
    for opp in opps:
        for i in range(num_seeds):
            seed = 100 + i
            p1_is_agent = (i % 2 == 0)
            tasks.append((agent_path, opp, seed, p1_is_agent))
            
    all_metrics = []
    rewards = []
    
    for i, t in enumerate(tasks):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(tasks)}")
        res = run_game(t)
        if res["status"] == "SUCCESS":
            rewards.append(res["reward"])
            if res.get("metrics"):
                all_metrics.append(res["metrics"])
                
    return rewards, all_metrics

def extract_metric(metrics_list, path_func):
    vals = []
    for m in metrics_list:
        try:
            v = path_func(m)
            if v is not None:
                vals.append(v)
        except (KeyError, TypeError, ZeroDivisionError):
            continue
    return np.mean(vals) if vals else 0

def generate_scorecard(variants_data):
    md = "# V018 Final Scorecard\n\n"
    
    md += "## Performance Summary\n"
    md += "| Variant | Mean Bank | Median | Std Dev | Min | Max | Diff vs V018-A |\n"
    md += "| ------- | --------: | -----: | ------: | --: | --: | -------------: |\n"
    
    a_mean = np.mean(variants_data["V018-A"]["rewards"])
    
    for name, data in variants_data.items():
        arr = np.array(data["rewards"])
        diff = np.mean(arr) - a_mean
        diff_str = f"${diff:+.2f}" if name != "V018-A" else "-"
        md += f"| {name} | ${np.mean(arr):.2f} | ${np.median(arr):.2f} | ${np.std(arr):.2f} | ${np.min(arr):.2f} | ${np.max(arr):.2f} | {diff_str} |\n"
        
    md += "\n## Detailed Metrics\n"
    
    cols = ["Variant", "Total Rev", "Seed Spend", "Worker Spend", "Land Spend", "Empty T-D", "Useful Acts", "Move Acts", "Idle", "Crop Death", "Water Miss", "Batch Size", "P_Plant", "P_Harv", "P_Recov", "Prem Rev", "Staple Rev", "Filler ROI"]
    md += "| " + " | ".join(cols) + " |\n"
    md += "|" + "|".join(["---:"] * len(cols)) + "|\n"
    
    for name, data in variants_data.items():
        mlist = data["metrics"]
        if not mlist:
            continue
            
        tot_rev = extract_metric(mlist, lambda m: m["economy"]["total_revenue"])
        seed_sp = extract_metric(mlist, lambda m: m["economy"]["seed_spending"])
        work_sp = extract_metric(mlist, lambda m: m["economy"]["worker_spending"])
        land_sp = extract_metric(mlist, lambda m: m["economy"].get("land_spending", 0))
        
        empty_td = extract_metric(mlist, lambda m: m.get("v018", {}).get("empty_tile_days", 0))
        useful = extract_metric(mlist, lambda m: m["farmer"]["useful_actions"] + m["workers"]["useful_actions"])
        moves = extract_metric(mlist, lambda m: m["farmer"]["movement_actions"] + m["workers"]["movement_actions"])
        idle = extract_metric(mlist, lambda m: m["farmer"]["idle_turns"] + m["workers"]["idle_turns"])
        
        deaths = extract_metric(mlist, lambda m: sum(c["deaths"] for c in m["crops"].values()))
        misses = extract_metric(mlist, lambda m: m["water"]["misses"])
        
        batches = extract_metric(mlist, lambda m: np.mean([b["qty"] for b in m.get("v018", {}).get("batches", [])]) if m.get("v018", {}).get("batches") else 0)
        
        p_plant = extract_metric(mlist, lambda m: np.mean(m.get("v018", {}).get("planting_prices", [])) if m.get("v018", {}).get("planting_prices") else 0)
        p_harv = extract_metric(mlist, lambda m: np.mean(m.get("v018", {}).get("harvest_prices", [])) if m.get("v018", {}).get("harvest_prices") else 0)
        p_recov = p_harv - p_plant
        
        prem_rev = extract_metric(mlist, lambda m: m.get("v018", {}).get("premium_revenue", 0))
        staple_rev = extract_metric(mlist, lambda m: m.get("v018", {}).get("staple_revenue", 0))
        
        def calc_roi(m):
            rev = m.get("v018", {}).get("filler_revenue", 0)
            seed = m.get("v018", {}).get("filler_seed_cost", 0)
            labor = m.get("v018", {}).get("filler_labor_cost", 0)
            if seed + labor > 0:
                return (rev - seed - labor) / (seed + labor)
            return 0
        roi = extract_metric(mlist, calc_roi) * 100
        
        row = [
            name,
            f"${tot_rev:.0f}",
            f"${seed_sp:.0f}",
            f"${work_sp:.0f}",
            f"${land_sp:.0f}",
            f"{empty_td:.0f}",
            f"{useful:.0f}",
            f"{moves:.0f}",
            f"{idle:.0f}",
            f"{deaths:.1f}",
            f"{misses:.1f}",
            f"{batches:.1f}",
            f"${p_plant:.1f}",
            f"${p_harv:.1f}",
            f"${p_recov:.1f}",
            f"${prem_rev:.0f}",
            f"${staple_rev:.0f}",
            f"{roi:.1f}%"
        ]
        md += "| " + " | ".join(row) + " |\n"
        
    with open("V018_SCORECARD.md", "w") as f:
        f.write(md)
    print("Saved V018_SCORECARD.md")

def main():
    print("Starting V018 Sweeps...")
    
    configs_b = {f"CAP_{c}": {"V018_B_CAP": c} for c in [2, 3, 4, 5, 6]}
    best_b_name, best_b_env = run_sweep("V018-B", "agents/v018_b_batch_cap.py", configs_b)
    
    configs_c = {}
    for target in [10, 15, 20, 25, 30]:
        for mech in ["C1_HARD", "C2_SOFT"]:
            configs_c[f"{mech}_T{target}"] = {"V018_C_TARGET": target, "V018_C_MECH": mech}
    best_c_name, best_c_env = run_sweep("V018-C", "agents/v018_c_inventory_pacing.py", configs_c)
    
    configs_d = {}
    for trigger in [5, 10, 15]:
        for mode in ["WHEAT_ONLY", "EV_BASED"]:
            configs_d[f"{mode}_T{trigger}"] = {"V018_D_TRIGGER": trigger, "V018_D_MODE": mode}
    best_d_name, best_d_env = run_sweep("V018-D", "agents/v018_d_subsistence.py", configs_d)
    
    print("\n==============================")
    print("Starting Final 360-game Benchmark")
    print("==============================")
    
    variants_data = {}
    opps = ["random", "pass", "starter"]
    num_seeds = 30
    
    print("Running V018-A...")
    r_a, m_a = analyze_benchmark("agents/v018_a_baseline.py", opps, num_seeds)
    variants_data["V018-A"] = {"rewards": r_a, "metrics": m_a}
    
    print(f"Running V018-B ({best_b_name})...")
    r_b, m_b = analyze_benchmark("agents/v018_b_batch_cap.py", opps, num_seeds, best_b_env)
    variants_data["V018-B"] = {"rewards": r_b, "metrics": m_b}
    
    print(f"Running V018-C ({best_c_name})...")
    r_c, m_c = analyze_benchmark("agents/v018_c_inventory_pacing.py", opps, num_seeds, best_c_env)
    variants_data["V018-C"] = {"rewards": r_c, "metrics": m_c}
    
    print(f"Running V018-D ({best_d_name})...")
    r_d, m_d = analyze_benchmark("agents/v018_d_subsistence.py", opps, num_seeds, best_d_env)
    variants_data["V018-D"] = {"rewards": r_d, "metrics": m_d}
    
    generate_scorecard(variants_data)

if __name__ == "__main__":
    main()
