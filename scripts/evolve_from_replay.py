"""
Targeted evolution from v092_replay_seed.py (156k Kaggle replay trace).

Goal: Evolve v092 into a robust agent that consistently scores 100k+
across all opponent types.

Strategy:
- Seed from v092_replay_seed (proven 156k strategy)
- Mutate at low rate (0.005) to preserve the winning sequence
- Fitness: 70% min score + 30% avg score (robustness focus)
- Opponents: v057, random, 013 (diverse pool)
- Run for 2 hours
"""
import json, base64, zlib, os, shutil, random, time, subprocess, multiprocessing
import sys

OPPONENTS = [
    "agents/v057_generalized_spoiler.py",
    "random",
    "agents/013_robust_trace.py",
]

def load_trace(path):
    with open(path, 'r') as f:
        code = f.read()
    # Extract the b85 encoded trace
    start = code.find("base64.b85decode(") + len("base64.b85decode(\n    '")
    end = code.find("'", start)
    if end < start:
        # Try single-line format
        start = code.find("b85decode('") + len("b85decode('")
        end = code.find("'", start)
    b85_str = code[start:end]
    compressed = base64.b85decode(b85_str)
    actions = json.loads(zlib.decompress(compressed))
    return actions, code

def compress_actions(actions):
    compressed = zlib.compress(json.dumps(actions).encode('utf-8'))
    return base64.b85encode(compressed).decode('utf-8')

def save_mutant(code, new_b85, worker_id):
    start = code.find("base64.b85decode(") + len("base64.b85decode(\n    '")
    end = code.find("'", start)
    if end < start:
        start = code.find("b85decode('") + len("b85decode('")
        end = code.find("'", start)
    new_code = code[:start] + new_b85 + code[end:]
    path = f"scratch/evolve_{worker_id}.py"
    os.makedirs("scratch", exist_ok=True)
    with open(path, 'w') as f:
        f.write(new_code)
    return path

def mutate(actions, rate=0.005):
    """Lightly mutate a trace to find improvements."""
    MOVES = ["NORTH", "SOUTH", "EAST", "WEST", "PASS"]
    new = [dict(a) for a in actions]
    
    for i in range(len(new)):
        if random.random() < rate:
            step = dict(new[i])
            # Mutate farmer action
            farmer = list(step.get("farmer", ["PASS"]))
            if farmer and farmer[0] in MOVES and random.random() < 0.5:
                farmer[0] = random.choice(MOVES)
                step["farmer"] = farmer
            # Mutate market: maybe add/remove/change a SELL order
            market = list(step.get("market", []))
            if market and random.random() < 0.3:
                idx = random.randrange(len(market))
                if market[idx][0] == "SELL" and len(market[idx]) >= 3:
                    qty = market[idx][2]
                    market[idx][2] = max(1, qty + random.randint(-3, 3))
                step["market"] = market
            new[i] = step
    return new

def evaluate_match(args):
    """Evaluate agent in ONE seat order. Returns agent's score."""
    agent_path, opp, agent_is_p0 = args
    if agent_is_p0:
        players = [agent_path, opp]
        seat = 0
    else:
        players = [opp, agent_path]
        seat = 1
    cmd = [
        sys.executable, "-c",
        f"from kaggle_environments import make; "
        f"env = make('kaggriculture', configuration={{'episodeSteps': 720}}, debug=False); "
        f"env.run({players}); "
        f"print(env.steps[-1][{seat}].reward)"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=35,
                             cwd=os.getcwd())
        return float(res.stdout.strip().split('\n')[-1])
    except Exception:
        return 0.0

def evaluate_all(agent_path):
    """Test in both seat orders against all opponents. Returns avg, min, list."""
    tasks = []
    for opp in OPPONENTS:
        tasks.append((agent_path, opp, True))   # agent as P0
        tasks.append((agent_path, opp, False))  # agent as P1
    with multiprocessing.Pool(processes=min(len(tasks), 6)) as pool:
        scores = pool.map(evaluate_match, tasks)
    return sum(scores) / len(scores), min(scores), scores

def main():
    seed_path = "agents/v092b_replay_seed.py"
    best_actions, base_code = load_trace(seed_path)
    
    print("=== Evolving from v092 replay seed ===")
    print(f"Opponents: {OPPONENTS}")
    
    # Evaluate baseline
    temp = save_mutant(base_code, compress_actions(best_actions), 0)
    best_avg, best_min, scores = evaluate_all(temp)
    best_fitness = best_min * 0.7 + best_avg * 0.3
    print(f"Baseline: avg={best_avg:.0f} min={best_min:.0f} scores={[f'{s:.0f}' for s in scores]}")
    
    iteration = 0
    end_time = time.time() + 3600 * 2  # 2 hours
    improved = 0
    
    while time.time() < end_time:
        iteration += 1
        mutated = mutate(best_actions, rate=0.005)
        b85 = compress_actions(mutated)
        temp = save_mutant(base_code, b85, 0)
        
        avg, mn, scores = evaluate_all(temp)
        fitness = mn * 0.7 + avg * 0.3
        
        print(f"Iter {iteration} | avg={avg:.0f} min={mn:.0f} scores={[f'{s:.0f}' for s in scores]}")
        
        if fitness > best_fitness:
            best_fitness = fitness
            best_avg, best_min = avg, mn
            best_actions = mutated
            improved += 1
            out = f"agents/v093_evolved_{improved:03d}.py"
            shutil.copy(temp, out)
            shutil.copy(temp, "agents/v093_evolved_best.py")
            print(f"  >> NEW BEST! fitness={fitness:.0f} saved to {out}")
    
    print(f"\nDone. {iteration} iterations, {improved} improvements.")
    print(f"Best: avg={best_avg:.0f} min={best_min:.0f} fitness={best_fitness:.0f}")

if __name__ == "__main__":
    main()
