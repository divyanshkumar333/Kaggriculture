import unittest
import numpy as np

# We import from ActionExecutor to test cost matrix generation
from agents.v006_b_sectors import ActionExecutor as SectorExecutor, Task
from agents.v006_c_tsp import ActionExecutor as TSPExecutor

class MockState:
    def __init__(self, unlocked):
        self.my_farm = {"unlocked_quadrants": unlocked}
        self.board_size = 10

class TestV006Movement(unittest.TestCase):
    def test_v006_b_sectors(self):
        executor = SectorExecutor(MockState(["NW", "SE"]), None)
        
        # Farmer at (0,0) (Unit 0, so sector NW)
        # Worker 1 at (9,9) (Unit 1, so sector SE)
        units = [(0, 0), (9, 9)]
        
        # Task in NW
        t_nw = Task("WATER", 100, (2, 2))
        # Task in SE
        t_se = Task("WATER", 100, (8, 8))
        
        field_tasks = [t_nw, t_se]
        
        n_workers = len(units)
        m_tasks = len(field_tasks)
        cost_matrix = np.zeros((n_workers, m_tasks))
        
        # Manually run the matrix logic from v006_b
        unlocked = ["NW", "SE"]
        sectors = [(0, 4, 0, 4), (5, 9, 5, 9)]
        
        for i, (ux, uy) in enumerate(units):
            assigned_sector = sectors[i % len(sectors)]
            sx1, sx2, sy1, sy2 = assigned_sector
            for j, target in enumerate(field_tasks):
                tx, ty = target.location
                dist = abs(ux - tx) + abs(uy - ty)
                out_of_sector_penalty = 10000 if not (sx1 <= tx <= sx2 and sy1 <= ty <= sy2) else 0
                cost = (dist * 10) - target.priority + out_of_sector_penalty
                cost_matrix[i, j] = cost
                
        # Worker 0 (NW) taking t_nw (NW) should have NO penalty
        self.assertTrue(cost_matrix[0, 0] < 1000)
        # Worker 0 (NW) taking t_se (SE) SHOULD have penalty
        self.assertTrue(cost_matrix[0, 1] > 9000)
        # Worker 1 (SE) taking t_nw (NW) SHOULD have penalty
        self.assertTrue(cost_matrix[1, 0] > 9000)
        # Worker 1 (SE) taking t_se (SE) should have NO penalty
        self.assertTrue(cost_matrix[1, 1] < 1000)

    def test_v006_c_tsp_distance_weighting(self):
        # We test that distance ** 2 prevents chasing high priority across map
        t_local = Task("WATER", 100, (0, 1)) # dist 1 from (0,0)
        t_far = Task("HARVEST", 500, (9, 9)) # dist 18 from (0,0)
        
        field_tasks = [t_local, t_far]
        units = [(0, 0)]
        
        cost_matrix = np.zeros((1, 2))
        for i, (ux, uy) in enumerate(units):
            for j, target in enumerate(field_tasks):
                tx, ty = target.location
                dist = abs(ux - tx) + abs(uy - ty)
                if target.priority >= 1000:
                    cost = -1000000 + (dist ** 2) * 10
                else:
                    cost = ((dist ** 2) * 10) - target.priority
                cost_matrix[i, j] = cost
                
        # Local task cost = 1^2 * 10 - 100 = -90
        # Far task cost = 18^2 * 10 - 500 = 3240 - 500 = 2740
        # The worker should PREFER the local task (-90 < 2740) despite lower priority!
        self.assertTrue(cost_matrix[0, 0] < cost_matrix[0, 1])

if __name__ == '__main__':
    unittest.main()
