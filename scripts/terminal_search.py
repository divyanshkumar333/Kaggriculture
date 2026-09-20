import sys
import json
import argparse
import itertools
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _safe(fn, obs, cfg):
    try:
        return fn(obs, cfg)
    except Exception:
        farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
        return {"farmer": ["PASS"],
                "hands": [["PASS"] for _ in (farm.get("hands") or [])],
                "market": []}

def main():
    ap = argparse.ArgumentParser(description="Terminal Search: Find optimal liquidation parameters.")
    ap.add_argument("replay", help="Path to replay JSON file")
    ap.add_argument("agent", help="Base agent to parameterize (must have _future_target function)")
    ap.add_argument("opponent", help="Opponent agent to test against")
    ap.add_argument("--step", type=int, default=600, help="Step to branch from (default: 600)")
    args = ap.parse_args()

    print(f"Loading replay: {args.replay}")
    with open(args.replay, "r") as f:
        replay_data = json.load(f)

    cfg = replay_data.get("configuration", {})
    steps = replay_data.get("steps", [])
    
    if args.step >= len(steps):
        print(f"Error: Requested step {args.step} is beyond replay length.")
        return 1
        
    branch_steps = steps[:args.step + 1]
    
    agent_mod = load_agent(args.agent)
    opp_mod = load_agent(args.opponent)
    
    if not hasattr(agent_mod, "_future_target"):
        print("Error: agent must have a _future_target function to parameterize.")
        return 1
        
    original_future_target = getattr(agent_mod, "_future_target")
    
    # Define our search space for the terminal phase
    depths = [1, 2, 3, 5, 8, 30]
    panic_selling_flags = [True, False]
    
    results = []
    
    import os
    from contextlib import redirect_stdout, redirect_stderr
    from kaggle_environments import make
    
    print(f"\nStarting Terminal Search from step {args.step}...")
    print(f"{'Depth':<10} | {'Panic Sell':<15} | {'Final Cash (A)':<15} | {'Delta vs B':<15}")
    print("-" * 60)
    
    for depth, panic in itertools.product(depths, panic_selling_flags):
        
        # Monkey patch the agent's _future_target
        def _patched_future_target(step, item, state):
            if panic:
                opp_shed = state.get("opp_shed", {})
                opp_qty = opp_shed.get(item, 0)
                if opp_qty >= 2:
                    return step + 1, opp_qty
            
            for offset in range(1, depth + 1):
                fut = step + offset
                if 0 <= fut < len(agent_mod._ACTIONS):
                    q = sum(max(0, int(o[2])) for o in agent_mod._ACTIONS[fut].get("market") or [] 
                            if len(o) >= 3 and o[0] == "SELL" and o[1] == item)
                    if q > 0:
                        return fut, q
            return None, 0
            
        agent_mod._future_target = _patched_future_target
        
        env = make("kaggriculture", configuration=cfg, steps=branch_steps, debug=False)
        
        with open(os.devnull, 'w') as f, redirect_stdout(f), redirect_stderr(f):
            env.run([lambda o, c: _safe(agent_mod.agent, o, c),
                     lambda o, c: _safe(opp_mod.agent, o, c)])
                     
        final_state = env.steps[-1]
        p0_reward = final_state[0].reward or 0
        p1_reward = final_state[1].reward or 0
        delta = p0_reward - p1_reward
        
        results.append({
            "depth": depth,
            "panic": panic,
            "cash": p0_reward,
            "delta": delta
        })
        
        print(f"{depth:<10} | {str(panic):<15} | ${p0_reward:<14.0f} | ${delta:<14.0f}")
        
    # Restore original function
    agent_mod._future_target = original_future_target
    
    best = max(results, key=lambda x: x["delta"])
    print("-" * 60)
    print(f"Optimal Terminal Parameters vs {Path(args.opponent).stem}:")
    print(f"Depth = {best['depth']}, Panic Selling = {best['panic']}")
    print(f"Expected Delta = ${best['delta']:,.0f}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
