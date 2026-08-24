import unittest
import copy
from agents.v010_b_land_expansion import DailyPlanner, StrategicPlanner, EconomicCalculator, GameState

class TestV010LandExpansion(unittest.TestCase):
    def setUp(self):
        self.base_state = {
            "player": 0,
            "step": 10,
            "day": 5,
            "hour": 5,
            "farms": [
                {
                    "money": 5000, # Lots of money
                    "farmer": [0, 0],
                    "hands": [],
                    "unlocked_quadrants": ["NW"],
                    "tiles": [[None]*10 for _ in range(10)]
                },
                {}
            ],
            "private": {
                "seeds": {"MELON": 0},
                "shed": {"MELON": 10}
            },
            "market": {},
            "town": {}
        }
        
    def _run_planner(self, state_dict):
        gs = GameState(state_dict)
        econ = EconomicCalculator(gs)
        strat = StrategicPlanner(gs, econ)
        planner = DailyPlanner(gs, econ, strat)
        return planner.plan_tasks()

    def test_buys_land_when_space_low_and_money_high(self):
        state = copy.deepcopy(self.base_state)
        for y in range(5):
            for x in range(5):
                state["farms"][0]["tiles"][y][x] = {"kind": "PLANT", "crop": "MELON", "planted_day": 1}
                
        state["farms"][0]["tiles"][0][0] = None
        state["farms"][0]["tiles"][0][1] = None
        state["farms"][0]["tiles"][1][0] = None
        state["farms"][0]["tiles"][1][1] = None
        
        for y in range(10):
            for x in range(10):
                if not (x < 5 and y < 5):
                    state["farms"][0]["tiles"][y][x] = "LOCKED"
        
        state["farms"][0]["money"] = 10000 
        
        tasks = self._run_planner(state)
        
        buy_land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(buy_land_tasks), 1)

    def test_does_not_buy_land_when_space_plentiful(self):
        state = copy.deepcopy(self.base_state)
        for y in range(10):
            for x in range(10):
                if not (x < 5 and y < 5):
                    state["farms"][0]["tiles"][y][x] = "LOCKED"
                    
        state["farms"][0]["money"] = 10000 
        
        tasks = self._run_planner(state)
        
        buy_land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(buy_land_tasks), 0)
        
    def test_does_not_buy_land_when_money_low(self):
        state = copy.deepcopy(self.base_state)
        for y in range(5):
            for x in range(5):
                state["farms"][0]["tiles"][y][x] = {"kind": "PLANT", "crop": "MELON", "planted_day": 1}
        state["farms"][0]["tiles"][0][0] = None
        state["farms"][0]["tiles"][0][1] = None
        state["farms"][0]["tiles"][1][0] = None
        state["farms"][0]["tiles"][1][1] = None
        
        for y in range(10):
            for x in range(10):
                if not (x < 5 and y < 5):
                    state["farms"][0]["tiles"][y][x] = "LOCKED"
                    
        state["farms"][0]["money"] = 100 
        
        tasks = self._run_planner(state)
        
        buy_land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(buy_land_tasks), 0)

if __name__ == "__main__":
    unittest.main()
