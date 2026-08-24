"""
Synthetic ablation tests for V013.
Tests each cost function variant in isolation against known scenarios.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

# ── minimal mock ─────────────────────────────────────────────────────────────
class Task:
    def __init__(self, location, priority=10):
        self.location = location
        self.priority = priority

def cost_baseline(units, tasks, prev=None):
    n, m = len(units), len(tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            C[i,j] = (-1_000_000 + dist*10) if t.priority >= 1000 else (dist*10 - t.priority)
    return C

def cost_b(units, tasks, prev=None):  # locality only
    C = cost_baseline(units, tasks, prev)
    for i, (ux, uy) in enumerate(units):
        u_quad = (ux//5, uy//5)
        for j, t in enumerate(tasks):
            tx, ty = t.location
            if (tx//5, ty//5) != u_quad:
                C[i,j] += 80
    return C

def cost_c(units, tasks, prev=None):  # locality + weak stability
    C = cost_b(units, tasks, prev)
    if prev:
        for i in range(len(units)):
            for j, t in enumerate(tasks):
                if prev.get(i) == t.location:
                    C[i,j] -= 10
    return C

def cost_d(units, tasks, prev=None):  # stability only
    C = cost_baseline(units, tasks, prev)
    if prev:
        for i in range(len(units)):
            for j, t in enumerate(tasks):
                if prev.get(i) == t.location:
                    C[i,j] -= 10
    return C

def assign(cost_fn, units, tasks, prev=None):
    C = cost_fn(units, tasks, prev)
    ri, ci = linear_sum_assignment(C)
    return {i: tasks[j].location for i, j in zip(ri, ci)}

# ── Tests ──────────────────────────────────────────────────────────────────
passed = 0

def check(name, cond):
    global passed
    if cond:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")

print("=== Test A: Local task beats equidistant cross-zone (B, C) ===")
units = [(4, 4)]  # NW quadrant
tasks = [Task((1,4)), Task((7,4))]  # dist-3 local (NW), dist-3 cross (NE)
for fn, name in [(cost_b, "B"), (cost_c, "C")]:
    a = assign(fn, units, tasks)
    check(f"Variant {name}: prefers local", a[0] == (1,4))

print("\n=== Test B: Cross-zone assigned when local is empty (B, C, D) ===")
units = [(4, 4)]
tasks = [Task((7, 4))]  # only a cross-zone task
for fn, name in [(cost_b, "B"), (cost_c, "C"), (cost_d, "D")]:
    a = assign(fn, units, tasks)
    check(f"Variant {name}: worker crosses zone if needed", a[0] == (7,4))

print("\n=== Test C: No stability = better assignment immediately replaces old (B) ===")
units = [(3, 3)]
# Originally heading to (4,3) dist=1. Now (1,3) is dist=2 but clearly same quadrant;
# more importantly: no stability means the solver is free to pick either optimally.
# Use a task at (3,1) (dist=2 away, same quadrant) vs stale (4,3) (dist=1).
# Without stability, (4,3) is cheaper (dist 1 < 2), so B should pick (4,3).
# The real property of B is: it does NOT add a stability penalty; the shortest wins.
# Test that B picks the shorter (4,3) without any stability locking.
prev = {0: (4,3)}
tasks_c = [Task((4,3)), Task((3,1))]  # (4,3)=dist1, (3,1)=dist2
a_b = assign(cost_b, units, tasks_c, prev)
check("Variant B: picks shortest-distance task, not stability-locked", a_b[0] == (4,3))

print("\n=== Test D: -10 stability cannot overpower 2-step shorter assignment (C, D) ===")
units = [(3, 3)]
# On (6,3) = dist 3 (cross-zone). New task at (2,3) = dist 1 (local).
# Cost of continuing (6,3) in C = 30 + 80 - 10 = 100
# Cost of (2,3) in C = 10 - 10(priority) = 0 + 0(no cross) = 10 - 10 = 0
# (2,3) must win.
prev = {0: (6,3)}
tasks = [Task((6,3)), Task((2,3))]
for fn, name in [(cost_c, "C"), (cost_d, "D")]:
    a = assign(fn, units, tasks, prev)
    check(f"Variant {name}: switches to clearly closer task", a[0] == (2,3))

print("\n=== Test E: Urgent task beats all locality/stability preferences (all) ===")
units = [(1, 1)]  # NW
tasks = [Task((2, 2), 10), Task((8, 8), 2000)]  # local ordinary, cross urgent
a_a = assign(cost_baseline, units, [tasks[1]])  # only urgent task
check("Baseline: urgent task gets assigned", a_a[0] == (8,8))
# With two workers: one local ordinary, one cross urgent
units2 = [(1,1), (7,7)]
for fn, name in [(cost_b, "B"), (cost_c, "C"), (cost_d, "D")]:
    a = assign(fn, units2, tasks)
    check(f"Variant {name}: urgent (8,8) assigned to someone", (8,8) in a.values())

print("\n=== Test F: No worker permanently trapped (B, C, D) ===")
# Worker in NW, only SE tasks remain
units = [(2, 2)]
tasks = [Task((7,7)), Task((8,8))]
for fn, name in [(cost_b, "B"), (cost_c, "C"), (cost_d, "D")]:
    a = assign(fn, units, tasks)
    check(f"Variant {name}: worker assigned cross-zone", a[0] in [(7,7),(8,8)])

print("\n=== Test G: D (stability only) assigns identically to baseline in same zone ===")
units = [(2, 2)]
tasks = [Task((1,1)), Task((3,3))]  # both NW, no prev
a_base = assign(cost_baseline, units, tasks)
a_d    = assign(cost_d, units, tasks)
check("Variant D: no stability, same zone => same assignment as baseline", a_base == a_d)

print(f"\n{passed} tests passed.")
