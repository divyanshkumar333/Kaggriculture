"""
train_v014.py - Evolve from 013_robust_trace using both seat orders.

Changes from train_robust_trace.py:
- Seeds from 013_robust_trace.py (our best proven agent, 960 Elo)
- Tests BOTH seat orders (P0 and P1) for each match
- Expanded opponent pool including v092b (top replay agent)
- Saves improvements as agents/014_robust_trace.py
- 3-hour run budget
"""
import os, json, base64, zlib, copy, random, time, multiprocessing, shutil, subprocess

OPPONENTS = [
    "agents/v057_generalized_spoiler.py",
    "agents/v092b_replay_seed.py",    # top replay agent
    "agents/v051_v16_lookahead30_final.py",
    "random",
]

def load_trajectory(agent_path):
    with open(agent_path, "r") as f:
        code = f.read()
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    b85_str = code[q1+1:q2]
    actions = json.loads(zlib.decompress(base64.b85decode(b85_str)))
    return actions, code

def mutate_trajectory(actions, mutation_rate=0.01):
    new_actions = copy.deepcopy(actions)
    for i in range(len(new_actions)):
        if random.random() < mutation_rate:
            market = new_actions[i].get("market", [])
            if market:
                idx = random.randint(0, len(market) - 1)
                order = market[idx]
                if order and len(order) >= 3 and type(order[2]) == int:
                    order[2] = max(1, order[2] + random.choice([-2, -1, 1, 2]))
                elif order and order[0] == "HIRE":
                    if random.random() < 0.3:
                        market.pop(idx)
    return new_actions

def evaluate_match(args):
    """Evaluate one match. agent_idx: 0=P0, 1=P1."""
    mutant_path, opponent, agent_idx = args
    if agent_idx == 0:
        players = [mutant_path, opponent]
    else:
        players = [opponent, mutant_path]
    cmd = [
        ".venv\\Scripts\\python", "-c",
        f"from kaggle_environments import make; "
        f"env=make('kaggriculture', debug=False); "
        f"env.run({players}); "
        f"print(env.steps[-1][{agent_idx}].reward)"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25,
                             cwd=os.getcwd())
        return float(res.stdout.strip().split('\n')[-1])
    except Exception:
        return 0.0

def save_and_evaluate(base_code, new_actions, worker_id):
    compressed = zlib.compress(json.dumps(new_actions).encode('utf-8'))
    b85_str = base64.b85encode(compressed).decode('utf-8')

    start = base_code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = base_code.find("'", start)
    q2 = base_code.find("'", q1 + 1)
    new_code = base_code[:q1+1] + b85_str + base_code[q2:]

    temp_path = f"scratch/v014_mutant_{worker_id}.py"
    os.makedirs("scratch", exist_ok=True)
    with open(temp_path, "w") as f:
        f.write(new_code)

    # Test both seat orders against all opponents
    tasks = []
    for opp in OPPONENTS:
        tasks.append((temp_path, opp, 0))  # P0
        tasks.append((temp_path, opp, 1))  # P1

    with multiprocessing.Pool(processes=min(len(tasks), 8)) as pool:
        scores = pool.map(evaluate_match, tasks)

    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    return avg_score, min_score, scores

def run():
    os.makedirs("scratch", exist_ok=True)
    seed = "agents/013_robust_trace.py"
    best_actions, base_code = load_trajectory(seed)
    best_avg, best_min, scores = save_and_evaluate(base_code, best_actions, 0)
    best_fitness = best_min * 0.7 + best_avg * 0.3
    print(f"Baseline (013) - Avg: {best_avg:.0f} | Min: {best_min:.0f} | Scores: {[f'{s:.0f}' for s in scores]}")
    print(f"Fitness: {best_fitness:.0f}")

    end_time = time.time() + 3600 * 3  # 3 hours
    iteration = 1
    improvements = 0

    while time.time() < end_time:
        new_actions = mutate_trajectory(best_actions, mutation_rate=0.01)
        avg_score, min_score, scores = save_and_evaluate(base_code, new_actions, 0)
        fitness = min_score * 0.7 + avg_score * 0.3

        print(f"Iter {iteration} | Avg: {avg_score:.0f} | Min: {min_score:.0f} | Scores: {[f'{s:.0f}' for s in scores]}")
        if fitness > best_fitness:
            best_fitness = fitness
            best_avg, best_min = avg_score, min_score
            best_actions = new_actions
            improvements += 1
            shutil.copy("scratch/v014_mutant_0.py", "agents/014_robust_trace.py")
            print(f"  -> NEW BEST #{improvements}! Fitness: {fitness:.0f}")

        iteration += 1

    print(f"\nDone. {iteration} iterations, {improvements} improvements.")
    print(f"Best: Avg={best_avg:.0f} Min={best_min:.0f} Fitness={best_fitness:.0f}")

if __name__ == "__main__":
    run()
