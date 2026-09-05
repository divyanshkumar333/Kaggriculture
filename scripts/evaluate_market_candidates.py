import os
import random
import time
import sys
from kaggle_environments import make

# Initialize exactly once to avoid 600x overhead and 600x OpenSpiel warnings
env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)

def run_match(args):
    seed, agent_path, base_path, seat = args
    agents = [agent_path, base_path] if seat == 0 else [base_path, agent_path]
    
    try:
        env.run(agents)
        final_state = env.steps[-1]
        
        failed = False
        exception = None
        for i, s in enumerate(final_state):
            if s.status in ["ERROR", "TIMEOUT", "INVALID"]:
                failed = True
                exception = s.status
                
        r0 = final_state[0].reward or 0
        r1 = final_state[1].reward or 0
        
        delta = (r0 - r1) if seat == 0 else (r1 - r0)
        
        return {
            "seed": seed,
            "seat": seat,
            "delta": delta,
            "failed": failed,
            "exception": exception,
            "reward_agent": r0 if seat == 0 else r1,
            "reward_base": r1 if seat == 0 else r0,
        }
    except Exception as e:
        return {
            "seed": seed,
            "seat": seat,
            "delta": 0,
            "failed": True,
            "exception": str(e),
            "reward_agent": 0,
            "reward_base": 0
        }

if __name__ == "__main__":
    candidates = [
        ("V028-market-A (Premium Lead)", "agents/v028_market_a.py"),
        ("V028-market-B (Impact Ordering)", "agents/v028_market_b.py"),
        ("V028-market-C (Both)", "agents/v028_market_c.py"),
    ]
    base_agent = "agents/v027_hierarchical_meta.py"
    
    num_seeds = 100
    random.seed(42)
    seeds = [random.randint(10000, 999999) for _ in range(num_seeds)]
    
    results = {c[0]: [] for c in candidates}
    
    print(f"Starting Kaggle Evaluation Tournament: {len(candidates)} candidates, {num_seeds} seeds x 2 seats", flush=True)
    start_time = time.time()
    
    for name, path in candidates:
        print(f"\\n============================================================", flush=True)
        print(f"EVALUATING: {name} vs V027", flush=True)
        print(f"============================================================", flush=True)
        
        tasks = []
        for seed in seeds:
            tasks.append((seed, path, base_agent, 0))
            tasks.append((seed, path, base_agent, 1))
            
        match_results = []
        for i, t in enumerate(tasks):
            res = run_match(t)
            match_results.append(res)
            if (i+1) % 20 == 0:
                print(f"Completed {i+1}/{len(tasks)} matches...", flush=True)
        
        # Aggregate pairs
        paired = {}
        failures = 0
        for r in match_results:
            seed = r["seed"]
            if seed not in paired:
                paired[seed] = {"0": None, "1": None}
            paired[seed][str(r["seat"])] = r
            if r["failed"]:
                failures += 1
                
        deltas = []
        wins = 0
        for seed, res in paired.items():
            s0 = res["0"]
            s1 = res["1"]
            if s0 and s1:
                avg_delta = (s0["delta"] + s1["delta"]) / 2.0
                deltas.append(avg_delta)
                if avg_delta > 0:
                    wins += 1
                    
        deltas.sort()
        
        mean_delta = sum(deltas) / len(deltas) if deltas else 0
        med_delta = deltas[len(deltas)//2] if deltas else 0
        p10 = deltas[int(len(deltas)*0.1)] if deltas else 0
        p90 = deltas[int(len(deltas)*0.9)] if deltas else 0
        
        print(f"Candidate: {name}", flush=True)
        print(f"Win Rate:  {wins}/{num_seeds} ({(wins/num_seeds)*100:.1f}%)", flush=True)
        print(f"Failures:  {failures}/{num_seeds*2} matches crashed", flush=True)
        print(f"Mean Pair: {mean_delta:.1f} coins", flush=True)
        print(f"Med Pair:  {med_delta:.1f} coins", flush=True)
        print(f"P10/P90:   {p10:.1f} / {p90:.1f}", flush=True)
        
        results[name] = {
            "wins": wins,
            "failures": failures,
            "mean": mean_delta,
            "med": med_delta,
            "p10": p10,
            "p90": p90
        }
        
    print("\\n\\nFINAL EVALUATION SUMMARY", flush=True)
    for name, r in results.items():
        print(f"{name.ljust(35)} | {r['wins']:3d}/{num_seeds} W | Mean: {r['mean']:8.1f} | Failures: {r['failures']}", flush=True)
    
    print(f"Tournament completed in {time.time() - start_time:.1f} seconds", flush=True)
