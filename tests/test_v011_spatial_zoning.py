import unittest
import copy
from agents.v011_b_spatial_zoning import ActionExecutor, GameState, Task

class TestV011SpatialZoning(unittest.TestCase):
    def setUp(self):
        # We simulate a state with all 4 quadrants unlocked, and 4 workers.
        # Worker 0 (farmer), Worker 1, 2, 3 (hands)
        self.state_dict = {
            "player": 0,
            "step": 10,
            "day": 5,
            "hour": 5,
            "farms": [
                {
                    "money": 5000,
                    "farmer": [1, 1], # NW
                    "hands": [
                        [6, 1], # NE
                        [1, 6], # SW
                        [6, 6]  # SE
                    ],
                    "unlocked_quadrants": ["NW", "NE", "SW", "SE"],
                    "tiles": [[None]*10 for _ in range(10)]
                },
                {}
            ],
            "private": {
                "seeds": {},
                "shed": {}
            },
            "market": {},
            "town": {}
        }
        self.state = GameState(self.state_dict)
        # We don't actually need the economic calculator for execution testing
        self.executor = ActionExecutor(self.state, None)
        
    def test_strict_quadrant_assignment(self):
        # We have 4 workers.
        # Index 0 (NW worker), Index 1 (NE worker), Index 2 (SW worker), Index 3 (SE worker)
        
        # We create 2 tasks: One in NW, one in SE
        task_nw = Task("WATER", priority=1500, kwargs={}, location=(2, 2))
        task_se = Task("WATER", priority=1500, kwargs={}, location=(8, 8))
        
        # We also put the SE worker right next to the NW task, just to see if the matching
        # would normally try to drag them over there if distance was the only factor!
        # Worker 3 (SE) is currently at (6,6), distance to (2,2) is 4 + 4 = 8.
        # Wait, if we move the SE worker to (3,3) which is in NW... No, if the worker is physically in NW, 
        # their ASSIGNED quadrant is still SE (because unlocked_quads[3] == "SE").
        # So they MUST be assigned to the SE task, even if they are physically sitting on top of the NW task.
        
        self.state.hands[2] = [2, 3] # SE worker physically moved to NW
        
        result = self.executor.execute([task_nw, task_se], [])
        
        action_se = result["hands"][2][0] if len(result["hands"]) > 2 else "PASS"
        self.assertIn(action_se, ["EAST", "SOUTH", "WEST", "NORTH", "PASS", "WATER"])
        self.assertNotEqual(action_se, "PASS") # They must move towards (8,8)
        
        # NW worker is index 0 (farmer). They are at (1,1). Their task is (2,2) in NW.
        action_nw = result["farmer"][0]
        self.assertNotEqual(action_nw, "PASS") # They must move towards (2,2)
        
    def test_unassigned_due_to_zone(self):
        # Only a task in NW exists.
        task_nw = Task("WATER", priority=1500, kwargs={}, location=(2, 2))
        
        # Only SE worker exists! (Farmer is index 0, so unlocked_quads[0] == "NW")
        # Wait, farmer is ALWAYS index 0. So farmer gets NW.
        # Let's say unlocked quadrants = ["SE"].
        self.state.my_farm["unlocked_quadrants"] = ["SE"]
        
        # Now farmer (index 0) gets SE.
        # There is a task in NW.
        result = self.executor.execute([task_nw], [])
        
        # The farmer (assigned to SE) should NOT take the NW task.
        self.assertEqual(result["farmer"][0], "PASS")
        
if __name__ == "__main__":
    unittest.main()
