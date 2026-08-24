"""
V013 attribution profiler.
Runs 5 games each for V012-A (control) and V012-B (soft affinity)
and records detailed per-turn assignment statistics.
"""
import sys, os, importlib.util, collections
import numpy as np
from scipy.optimize import linear_sum_assignment

os.chdir(r"e:\Setup\kaggle\kaggriculture")
from kaggle_environments import make

# ── helpers ─────────────────────────────────────────────────────────────────
def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent_module", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["agent_module"] = mod
    spec.loader.exec_module(mod)
    return mod

def build_cost_baseline(units, field_tasks):
    """Vanilla V012-A / V010-B cost: dist*10 - priority, urgency override."""
    n, m = len(units), len(field_tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(field_tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            if t.priority >= 1000:
                C[i,j] = -1_000_000 + dist*10
            else:
                C[i,j] = dist*10 - t.priority
    return C

def build_cost_v012b(units, field_tasks, prev_assignments):
    """V012-B cost: +80 cross-quadrant, -40 stability."""
    n, m = len(units), len(field_tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        u_quad = (ux//5, uy//5)
        for j, t in enumerate(field_tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            if t.priority >= 1000:
                cost = -1_000_000 + dist*10
            else:
                cost = dist*10 - t.priority
            t_quad = (tx//5, ty//5)
            if u_quad != t_quad:
                cost += 80
            if prev_assignments.get(i) == (tx, ty):
                cost -= 40
            C[i,j] = cost
    return C

# ── profiling state ──────────────────────────────────────────────────────────
def new_stats():
    return {
        "total_assignments": 0,
        "cross_quadrant": 0,
        "local": 0,
        "stability_kept":   0,   # stability bonus kept the same target
        "stability_changed": 0,  # stability bonus was present but worker changed anyway
        "stability_overrode_shorter": 0,  # worker stayed on longer path due to stability
        "urgent_cross": 0,
        "idle_turns": 0,
        "reassignments": 0,
        "total_dist_at_assignment": 0,
    }

def profile_one_game(agent_path, variant_cost_fn, seed):
    """Run one game, intercept the assignment loop, collect stats."""
    mod = load_agent(agent_path)
    ActionExecutor = mod.ActionExecutor
    orig_execute = ActionExecutor.execute

    stats = new_stats()
    prev_assignments = {}   # worker_idx -> (tx, ty)

    def patched_execute(self, tasks, assignments):
        field_tasks = [t for t in tasks if t.location is not None]
        units = [self.state.farmer] + self.state.hands

        if field_tasks and units:
            C = variant_cost_fn(units, field_tasks, prev_assignments)
            row_ind, col_ind = linear_sum_assignment(C)

            for i, j in zip(row_ind, col_ind):
                t = field_tasks[j]
                ux, uy = units[i]
                tx, ty = t.location

                u_quad = (ux//5, uy//5)
                t_quad = (tx//5, ty//5)

                stats["total_assignments"] += 1
                if u_quad != t_quad:
                    stats["cross_quadrant"] += 1
                    if t.priority >= 1000:
                        stats["urgent_cross"] += 1
                else:
                    stats["local"] += 1

                prev_loc = prev_assignments.get(i)
                curr_loc = (tx, ty)

                if prev_loc is not None and prev_loc != curr_loc:
                    stats["reassignments"] += 1
                    # Was the previous target still in the task pool? If so, stability bonus
                    # could have kept us there but didn't (or did with baseline).
                prev_assignments[i] = curr_loc

                stats["total_dist_at_assignment"] += abs(ux-tx) + abs(uy-ty)

            idle_this_turn = len(units) - len(row_ind)
            stats["idle_turns"] += idle_this_turn

        return orig_execute(self, tasks, assignments)

    ActionExecutor.execute = patched_execute
    os.environ["KAGGRICULTURE_SEED"] = f"{seed}_profile"

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([mod.agent, "random"])

    ActionExecutor.execute = orig_execute
    return stats

# ── run profile ──────────────────────────────────────────────────────────────
SEEDS = [42, 43, 44, 45, 46]
AGENTS = {
    "v012_a": ("agents/v012_a_control.py", lambda u, t, p: build_cost_baseline(u, t)),
    "v012_b": ("agents/v012_b_soft_affinity.py", build_cost_v012b),
}

print("Profiling V012-A and V012-B over 5 games each...\n")

all_results = {}
for name, (path, cost_fn) in AGENTS.items():
    agg = new_stats()
    for seed in SEEDS:
        s = profile_one_game(path, cost_fn, seed)
        for k in agg:
            agg[k] += s[k]
    all_results[name] = agg
    print(f"\n=== {name} (aggregated over {len(SEEDS)} games) ===")
    print(f"  Total assignments      : {agg['total_assignments']}")
    print(f"  Local                  : {agg['local']}  ({100*agg['local']/max(1,agg['total_assignments']):.1f}%)")
    print(f"  Cross-quadrant         : {agg['cross_quadrant']}  ({100*agg['cross_quadrant']/max(1,agg['total_assignments']):.1f}%)")
    print(f"    Urgent cross-zone    : {agg['urgent_cross']}")
    print(f"  Reassignments          : {agg['reassignments']}  ({100*agg['reassignments']/max(1,agg['total_assignments']):.1f}%)")
    print(f"  Idle worker-turns      : {agg['idle_turns']}")
    print(f"  Avg dist at assignment : {agg['total_dist_at_assignment']/max(1,agg['total_assignments']):.2f}")

print("\nDelta (v012_b - v012_a):")
a = all_results["v012_a"]
b = all_results["v012_b"]
for k in a:
    if k in ("total_assignments",):
        continue
    da = a[k] / max(1, a["total_assignments"])
    db = b[k] / max(1, b["total_assignments"])
    print(f"  {k:35s}: {da:+.3f} → {db:+.3f}  (Δ {db-da:+.3f})")
