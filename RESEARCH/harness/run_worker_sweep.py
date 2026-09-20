import os
import json
import logging
import sys
from contextlib import redirect_stdout, redirect_stderr
from kaggle_environments import make

logging.getLogger("kaggle_environments").setLevel(logging.CRITICAL)

def evaluate_match(candidate, opponent, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    try:
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([candidate, opponent])
        p0_reward = env.steps[-1][0].reward or 0
        p1_reward = env.steps[-1][1].reward or 0
        return 1 if p0_reward > p1_reward else 0.5 if p0_reward == p1_reward else 0
    except Exception:
        return 0

def create_patched_agent(base_path, target_workers, temp_path):
    with open(base_path, 'r') as f:
        code = f.read()
    
    # Simple monkey-patch strategy: just replace max hires constants
    # V025-A usually has a _MAX_HIRES = X or similar. We will just append a wrapper
    # that overrides the config or state if possible. 
    # Alternatively, the easiest way to cap workers dynamically is to intercept the agent return 
    # and strip out "HIRE" orders if worker count >= target_workers.
    
    wrapper = f"""
{code}

# Overridden agent entrypoint for worker cap sweep
_original_agent = agent

def agent(obs, conf=None):
    import copy
    my_farm = obs["farms"][obs["player"]]
    hires_today = my_farm.get("hires_today", 0)
    current_hands = len(my_farm.get("hands", []))
    
    # Total workers = 1 farmer + current_hands
    total_workers = 1 + current_hands
    
    act = _original_agent(obs, conf)
    
    target_cap = {target_workers}
    if total_workers >= target_cap:
        # Strip HIRE
        new_market = []
        for order in act.get("market", []):
            if order and order[0] == "HIRE":
                continue
            new_market.append(order)
        act["market"] = new_market
        
    return act
"""
    with open(temp_path, 'w') as f:
        f.write(wrapper)
        
def main():
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agents"))
    base_agent = os.path.join(agents_dir, "v025_a_aggressive_cows.py")
    
    meta_panel = [
        os.path.join(agents_dir, "v025_a_aggressive_cows.py"),
        os.path.join(agents_dir, "v059_strawberry_flywheel.py"),
        "random"
    ]
    
    worker_caps = list(range(6, 15))
    seeds = [100, 200] # minimal sweep
    
    results = {}
    
    for cap in worker_caps:
        print(f"Sweeping max {cap} workers...")
        temp_agent_path = os.path.join(os.path.dirname(__file__), f"temp_agent_{cap}.py")
        create_patched_agent(base_agent, cap, temp_agent_path)
        
        win_score = 0
        total_matches = len(meta_panel) * len(seeds)
        
        for opp in meta_panel:
            for s in seeds:
                score = evaluate_match(temp_agent_path, opp, s)
                win_score += score
                
        results[cap] = {
            "win_score": win_score,
            "total_matches": total_matches,
            "win_rate": win_score / total_matches
        }
        
        if os.path.exists(temp_agent_path):
            os.remove(temp_agent_path)
            
    print("\nWORKER SWEEP RESULTS:")
    for cap, res in results.items():
        print(f"Cap {cap}: {res['win_score']}/{res['total_matches']} ({res['win_rate']:.2f})")

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports", "WORKER_SWEEP_RESULTS.json"))
    with open(out_path, "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
