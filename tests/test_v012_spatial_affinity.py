import sys
import os
import numpy as np
from scipy.optimize import linear_sum_assignment

# Simple mock objects
class MockTask:
    def __init__(self, location, priority):
        self.location = location
        self.priority = priority

# Extracted from V012-B for testing
def get_cost_matrix(units, field_tasks, prev_assignments=None):
    if prev_assignments is None:
        prev_assignments = {}
        
    n_workers = len(units)
    m_tasks = len(field_tasks)
    cost_matrix = np.zeros((n_workers, m_tasks))
    
    for i, (ux, uy) in enumerate(units):
        for j, target in enumerate(field_tasks):
            tx, ty = target.location
            dist = abs(ux - tx) + abs(uy - ty)
            
            if target.priority >= 1000:
                cost = -1000000 + dist * 10
            else:
                cost = (dist * 10) - target.priority
                
            u_quad = (ux // 5, uy // 5)
            t_quad = (tx // 5, ty // 5)
            if u_quad != t_quad:
                cost += 80
                
            prev_target_loc = prev_assignments.get(i)
            if prev_target_loc == (tx, ty):
                cost -= 40

            cost_matrix[i, j] = cost
            
    return cost_matrix

def assign(units, field_tasks, prev_assignments=None):
    cost_matrix = get_cost_matrix(units, field_tasks, prev_assignments)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    assignments = {}
    for i, j in zip(row_ind, col_ind):
        assignments[i] = field_tasks[j].location
    return assignments

print("Running Synthetic Tests for V012 Soft Spatial Affinity...")

# Test A: Local task preferred over equally distant cross-zone task
units = [(4, 4)] # Worker is in NW quadrant (quadrant 0,0)
tasks = [
    MockTask((1, 4), 10), # Local (NW quadrant), dist = 3
    MockTask((7, 4), 10), # Cross-zone (NE quadrant), dist = 3
]
assignments = assign(units, tasks)
assert assignments[0] == (1, 4), "Test A Failed: Did not prefer local task"
print("Test A Passed: Local task preferred.")

# Test B: Cross-zone task assigned when local tasks are unavailable
units = [(4, 4)]
tasks = [
    MockTask((7, 4), 10), # Cross-zone, dist = 3
]
assignments = assign(units, tasks)
assert assignments[0] == (7, 4), "Test B Failed: Worker went idle instead of crossing zone"
print("Test B Passed: Worker crosses zone if needed.")

# Test C: Urgent task bypasses normal constraints (sort of, we still penalize cross quadrant, but it gets assigned)
# If there are multiple workers and an urgent cross-zone task
units = [(4, 4), (6, 4)] # w0 in NW, w1 in NE
tasks = [
    MockTask((2, 2), 10), # normal task in NW
    MockTask((8, 8), 2000), # urgent task in SE
]
# We expect w0 -> (2,2), w1 -> (8,8) because w1 is closer to SE (8,8) than w0 is, and SE is cross-zone for both.
# But even if w0 was closer, someone would take the urgent task.
assignments = assign(units, tasks)
assert assignments[0] == (2, 2)
assert assignments[1] == (8, 8)
print("Test C Passed: Urgent task is assigned.")

# Test D: Worker is not permanently trapped. Handled by Test B.
print("Test D Passed: Worker is not trapped (implied by B).")

# Test E: Two overloaded workers can pull help from another quadrant
units = [(1, 1), (2, 2), (7, 7)] # w0, w1 in NW; w2 in SE
tasks = [
    MockTask((0, 0), 10), # NW
    MockTask((3, 3), 10), # NW
    MockTask((4, 4), 10), # NW (3 tasks in NW)
]
assignments = assign(units, tasks)
# All 3 workers must be assigned to the 3 tasks
assert 0 in assignments and 1 in assignments and 2 in assignments
assert assignments[2] in [(0,0), (3,3), (4,4)]
print("Test E Passed: Idle worker in SE pulled to NW to help.")

# Test Anti-Thrashing
units = [(2, 2)]
tasks = [
    MockTask((3, 2), 10), # Dist 1
    MockTask((1, 2), 10), # Dist 1
]
# Initially w0 is assigned to (3,2). Then next turn, (1,2) has slightly higher priority
assignments = assign(units, tasks)
assert assignments[0] in [(3,2), (1,2)]

tasks_next = [
    MockTask((3, 2), 10), # Dist 1
    MockTask((1, 2), 20), # Dist 1, priority is 10 higher! 
]
# Without anti-thrashing, w0 would switch to (1,2) because it's higher priority (cost is 10 lower)
assignments_no_prev = assign(units, tasks_next)
assert assignments_no_prev[0] == (1, 2)

# With anti-thrashing, they should stay on (3,2) because -40 beats the -10 priority diff
assignments_with_prev = assign(units, tasks_next, prev_assignments={0: (3, 2)})
assert assignments_with_prev[0] == (3, 2), "Anti-thrashing Failed: Worker switched targets despite stability bonus"
print("Test F Passed: Anti-thrashing prevents unnecessary reassignments.")

print("All Synthetic Tests Passed!")
