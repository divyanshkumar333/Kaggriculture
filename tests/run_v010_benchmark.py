import os
import subprocess
import json
import statistics
import multiprocessing

def run_game(args):
    agent, opponent, seed = args
    cmd = [
        ".venv\\Scripts\\python.exe", "experiments.py",
        "--agent", agent,
        "--opponent", opponent,
        "--games", "1",
        "--seed_start", str(seed)
    ]
    # We want to suppress output to keep console clean
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Game failed for {agent} vs {opponent} (seed {seed}):\n{e.stderr}")
        return None
    
    # After the game, read the single-game results.json to extract the final bank
    # experiments.py writes to experiments/results.json
    try:
        with open("experiments/results.json") as f:
            res = json.load(f)
        
        # Read the metrics file for player 0 (our agent)
        metrics_file = f"experiments/metrics/game_{seed}_p0.json"
        metrics = {}
        if os.path.exists(metrics_file):
            with open(metrics_file) as f:
                metrics = json.load(f)
            os.remove(metrics_file) # cleanup
            
        metrics_file_p1 = f"experiments/metrics/game_{seed}_p1.json"
        if os.path.exists(metrics_file_p1):
            os.remove(metrics_file_p1)
            
        final_money = res.get(agent, {}).get("mean", 0)
        return {"agent": agent, "opponent": opponent, "seed": seed, "final_money": final_money, "metrics": metrics}
    except Exception as e:
        print(f"Error parsing results for seed {seed}: {e}")
        return None

if __name__ == "__main__":
    agents = ["agents/v010_a_control.py", "agents/v010_b_land_expansion.py"]
    opponents = ["random", "starter", "agents/melon_maxxer.py"]
    games = 30
    start_seed = 3000
    
    tasks = []
    for agent in agents:
        for opp in opponents:
            for i in range(games):
                seed = start_seed + i
                tasks.append((agent, opp, seed))
                
    # Clean up results.json before starting
    if os.path.exists("experiments/results.json"):
        os.remove("experiments/results.json")
        
    print(f"Starting V010 benchmark: {len(tasks)} games total...")
    
    # Run sequentially to avoid race conditions on experiments/results.json
    results = []
    for i, task in enumerate(tasks):
        res = run_game(task)
        if res:
            results.append(res)
        if (i + 1) % 10 == 0:
            print(f"Completed {i+1}/{len(tasks)} games")
                
    # Process results
    analysis = {a: {"OVERALL": {"raw": {"final_money": [], "total_revenue": [], "seed_spending": [], "worker_spending": [], "crop_deaths": [], "water_misses": [], "hired": [], "useful_actions": [], "movement_actions": [], "movement_efficiency": [], "idle_turns": [], "unlocked_tiles": [], "land_spending": []}}} for a in agents}
    
    for r in results:
        a = r["agent"]
        m = r["metrics"]
        
        o = analysis[a]["OVERALL"]["raw"]
        o["final_money"].append(r["final_money"])
        
        if m:
            o["total_revenue"].append(m.get("economy", {}).get("total_revenue", 0))
            o["seed_spending"].append(m.get("economy", {}).get("seed_spending", 0))
            o["worker_spending"].append(m.get("economy", {}).get("worker_spending", 0))
            o["land_spending"].append(m.get("economy", {}).get("land_spending", 0))
            
            deaths = sum(c.get("deaths", 0) for c in m.get("crops", {}).values())
            o["crop_deaths"].append(deaths)
            o["water_misses"].append(m.get("water", {}).get("misses", 0))
            
            o["hired"].append(m.get("workers", {}).get("hired", 0))
            u = m.get("workers", {}).get("useful_actions", 0) + m.get("farmer", {}).get("useful_actions", 0)
            mov = m.get("workers", {}).get("movement_actions", 0) + m.get("farmer", {}).get("movement_actions", 0)
            
            o["useful_actions"].append(u)
            o["movement_actions"].append(mov)
            if u + mov > 0:
                o["movement_efficiency"].append(u / (u + mov))
            else:
                o["movement_efficiency"].append(0)
                
            o["idle_turns"].append(m.get("workers", {}).get("idle_turns", 0))
            
            o["unlocked_tiles"].append(m.get("land", {}).get("unlocked", 0)) # Actually we should extract this from game state if possible. 
            
    for a in agents:
        o = analysis[a]["OVERALL"]
        raw = o["raw"]
        o["mean"] = {}
        for k, v in raw.items():
            if v:
                o["mean"][k] = statistics.mean(v)
            else:
                o["mean"][k] = 0
                
    with open("experiments/v010_benchmark_full.json", "w") as f:
        json.dump(analysis, f, indent=2)
        
    print("\nBenchmark Complete!")
    for a in agents:
        print(f"\n{a} Mean Final Bank: ${analysis[a]['OVERALL']['mean']['final_money']:.2f}")
