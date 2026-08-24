import sys
import os
import importlib.util
from kaggle_environments import make

# Load the agent module
spec = importlib.util.spec_from_file_location("agent_module", "agents/v011_a_control.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["agent_module"] = agent_module
spec.loader.exec_module(agent_module)

ActionExecutor = agent_module.ActionExecutor
original_execute = ActionExecutor.execute

profiler = {
    "cross_quadrant": 0,
    "local": 0,
    "cross_quadrant_urgent": 0,
    "idle": 0,
    "reassignments": 0,
    "worker_assignments": {}, # worker_id -> target_loc
    "total_tasks_assigned": 0
}

def patched_execute(self, tasks, assignments):
    # Call original execute to let it do the assignment
    # Wait, original execute also mutates state and returns actions, but the assigned_targets is internal.
    # To get the assignment, we can look at the returned actions or re-run the assignment logic here.
    
    # Actually, it's easier to just re-run the assignment logic for profiling
    field_tasks = []
    for t in tasks:
        if t.location is not None:
            field_tasks.append(t)
            
    units = [self.state.farmer] + self.state.hands
    
    if field_tasks and units:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
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
                cost_matrix[i, j] = cost
                
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        for i, j in zip(row_ind, col_ind):
            target = field_tasks[j]
            ux, uy = units[i]
            tx, ty = target.location
            
            u_quad_x, u_quad_y = ux // 5, uy // 5
            t_quad_x, t_quad_y = tx // 5, ty // 5
            
            profiler["total_tasks_assigned"] += 1
            if u_quad_x != t_quad_x or u_quad_y != t_quad_y:
                profiler["cross_quadrant"] += 1
                if target.priority >= 1000:
                    profiler["cross_quadrant_urgent"] += 1
            else:
                profiler["local"] += 1
                
            prev_loc = profiler["worker_assignments"].get(i)
            curr_loc = (tx, ty)
            if prev_loc is not None and prev_loc != curr_loc:
                profiler["reassignments"] += 1
            profiler["worker_assignments"][i] = curr_loc
            
        idle_this_turn = len(units) - len(row_ind)
        profiler["idle"] += idle_this_turn

    return original_execute(self, tasks, assignments)

ActionExecutor.execute = patched_execute

print("Running 3 games to collect bottleneck data...")
for i in range(3):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42 + i}, debug=False)
    env.run([agent_module.agent, "random"])
    print(f"Game {i+1} done.")

print("\n--- V012 BOTTLENECK ANALYSIS (V011-A Control) ---")
print(f"Total Tasks Assigned: {profiler['total_tasks_assigned']}")
print(f"Local Assignments: {profiler['local']}")
print(f"Cross-Quadrant Assignments: {profiler['cross_quadrant']}")
print(f"  - Urgent Cross-Quadrant: {profiler['cross_quadrant_urgent']}")
print(f"  - Non-Urgent Cross-Quadrant: {profiler['cross_quadrant'] - profiler['cross_quadrant_urgent']}")
print(f"Reassignments (Thrashing): {profiler['reassignments']}")
print(f"Idle Worker Turns: {profiler['idle']}")

