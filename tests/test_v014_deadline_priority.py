"""
Synthetic tests for V014 Deadline-Aware Task Prioritization.
Tests each cost function variant in isolation against known scenarios.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

class Task:
    def __init__(self, location, priority=10, kwargs=None):
        self.location = location
        self.priority = priority
        self.kwargs = kwargs or {}

def cost_a(units, tasks):  # control
    n, m = len(units), len(tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            C[i,j] = (-1_000_000 + dist*10) if t.priority >= 1000 else (dist*10 - t.priority)
    return C

def cost_b(units, tasks):  # deadline only
    n, m = len(units), len(tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            if t.priority >= 1000:
                C[i,j] = -1_000_000 + dist*10
            else:
                C[i,j] = (dist*10) - t.priority - t.kwargs.get("urgency_score", 0)
    return C

def cost_c(units, tasks):  # economic only
    n, m = len(units), len(tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            if t.priority >= 1000:
                C[i,j] = -1_000_000 + dist*10
            else:
                C[i,j] = (dist*10) - t.priority - t.kwargs.get("value_score", 0)
    return C

def cost_d(units, tasks):  # combined
    n, m = len(units), len(tasks)
    C = np.zeros((n, m))
    for i, (ux, uy) in enumerate(units):
        for j, t in enumerate(tasks):
            tx, ty = t.location
            dist = abs(ux-tx) + abs(uy-ty)
            if t.priority >= 1000:
                C[i,j] = -1_000_000 + dist*10
            else:
                C[i,j] = (dist*10) - t.priority - t.kwargs.get("urgency_score", 0) - t.kwargs.get("value_score", 0)
    return C

def assign(cost_fn, units, tasks):
    C = cost_fn(units, tasks)
    ri, ci = linear_sum_assignment(C)
    return {i: tasks[j].location for i, j in zip(ri, ci)}

passed = 0
def check(name, cond):
    global passed
    if cond:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")

print("=== Test 1: Near-death crop gets assigned over low-value nearby task (B, D) ===")
# Worker at (0,0)
# Task 1: PLANT nearby at (1,0) [dist 1, priority 30, urgency 0, value 20]
# Task 2: WATER dying melon at (8,0) [dist 8, priority 10, urgency 125, value 0]
units = [(0, 0)]
tasks = [
    Task((1, 0), priority=30, kwargs={"urgency_score": 0, "value_score": 20}),
    Task((8, 0), priority=10, kwargs={"urgency_score": 125, "value_score": 0})
]

# Control (A): Cost of PLANT = 10 - 30 = -20. Cost of WATER = 80 - 10 = +70. Chooses PLANT.
check("Variant A: ignores dying crop, picks nearby plant", assign(cost_a, units, tasks)[0] == (1,0))

# Deadline (B): Cost of PLANT = 10 - 30 - 0 = -20. Cost of WATER = 80 - 10 - 125 = -55. Chooses WATER.
check("Variant B: rescues dying crop", assign(cost_b, units, tasks)[0] == (8,0))

# Combined (D): Cost of PLANT = 10 - 30 - 0 - 20 = -40. Cost of WATER = 80 - 10 - 125 - 0 = -55. Chooses WATER.
check("Variant D: rescues dying crop despite value difference", assign(cost_d, units, tasks)[0] == (8,0))


print("\n=== Test 2: High-value harvest gets assigned over low-value task (C, D) ===")
# Worker at (0,0)
# Task 1: HARVEST wheat nearby at (2,0) [dist 2, priority 20, urgency 5, value 25]
# Task 2: HARVEST melon far at (8,0) [dist 8, priority 20, urgency 25, value 250]
units = [(0, 0)]
tasks = [
    Task((2, 0), priority=20, kwargs={"urgency_score": 5, "value_score": 25}),
    Task((8, 0), priority=20, kwargs={"urgency_score": 25, "value_score": 250})
]

# Control (A): Cost of Wheat = 20 - 20 = 0. Cost of Melon = 80 - 20 = 60. Chooses Wheat.
check("Variant A: ignores high value, picks nearby harvest", assign(cost_a, units, tasks)[0] == (2,0))

# Economic (C): Cost of Wheat = 20 - 20 - 25 = -25. Cost of Melon = 80 - 20 - 250 = -190. Chooses Melon.
check("Variant C: travels for high value", assign(cost_c, units, tasks)[0] == (8,0))

# Combined (D): Cost of Wheat = 20 - 20 - 5 - 25 = -30. Cost of Melon = 80 - 20 - 25 - 250 = -215. Chooses Melon.
check("Variant D: travels for high value", assign(cost_d, units, tasks)[0] == (8,0))


print("\n=== Test 3: Distance still dictates assignments when scores are comparable ===")
# Worker at (0,0)
# Task 1: WATER wheat at (2,0) [dist 2, priority 10, urgency 12, value 0]
# Task 2: WATER wheat at (8,0) [dist 8, priority 10, urgency 12, value 0]
units = [(0, 0)]
tasks = [
    Task((2, 0), priority=10, kwargs={"urgency_score": 12, "value_score": 0}),
    Task((8, 0), priority=10, kwargs={"urgency_score": 12, "value_score": 0})
]
for fn, name in [(cost_a, "A"), (cost_b, "B"), (cost_c, "C"), (cost_d, "D")]:
    check(f"Variant {name}: chooses closer identical task", assign(fn, units, tasks)[0] == (2,0))

print(f"\n{passed} tests passed.")
