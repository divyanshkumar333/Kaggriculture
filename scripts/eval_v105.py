import os
import sys
import time
import numpy as np
from kaggle_environments import make

def load_code(p):
    ns = {}
    with open(p, "r", encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, os.path.basename(p), "exec"), ns)
    callables = [v for v in ns.values() if callable(v)]
    return callables[-1]

def run_match(p0_path, p1_path, seed):
    a0 = load_code(p0_path)
    a1 = load_code(p1_path)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([a0, a1])
    r0 = float(env.steps[-1][0].get("reward", 0) or 0)
    r1 = float(env.steps[-1][1].get("reward", 0) or 0)
    return r0, r1

def main():
    v104 = r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py"
    v105 = r"e:\Setup\kaggle\kaggriculture\agents\v105_tomato_unlocked.py"
    seeds = [42, 101, 2024, 777, 9999, 123]
    
    print("=" * 60)
    print("EVALUATION: V105 (Tomato Unlocked) vs V104 (Quote Priority)")
    print("=" * 60)
    
    v105_w, v104_w, draws = 0, 0, 0
    diffs = []
    
    for s in seeds:
        # v105 as P0, v104 as P1
        r0, r1 = run_match(v105, v104, s)
        diffs.append(r0 - r1)
        if r0 > r1: v105_w += 1
        elif r1 > r0: v104_w += 1
        else: draws += 1
        print(f"Seed {s:5d} [V105 as P0]: V105=${r0:,.0f} | V104=${r1:,.0f} | Diff={r0-r1:+,.0f}")
        
        # v104 as P0, v105 as P1
        r0, r1 = run_match(v104, v105, s)
        diffs.append(r1 - r0)
        if r1 > r0: v105_w += 1
        elif r0 > r1: v104_w += 1
        else: draws += 1
        print(f"Seed {s:5d} [V105 as P1]: V105=${r1:,.0f} | V104=${r0:,.0f} | Diff={r1-r0:+,.0f}")
        
    print("-" * 60)
    print(f"V105: {v105_w}W - {v104_w}L - {draws}D | Mean Delta: ${np.mean(diffs):+,.0f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
