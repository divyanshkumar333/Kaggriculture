import unittest
import importlib.util
from kaggle_environments import make

spec_c = importlib.util.spec_from_file_location("v020_c_agent", "agents/v020_c_competitive_surgical.py")
v020_c_module = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(v020_c_module)

spec_v21d = importlib.util.spec_from_file_location("v021_d_agent", "agents/v021_d_throughput_scaling.py")
v021_d_module = importlib.util.module_from_spec(spec_v21d)
spec_v21d.loader.exec_module(v021_d_module)

class TestV021DThroughput(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation

    def test_stage_1_plant_cap_is_4(self):
        obs = dict(self.raw_obs)
        obs["day"] = 3
        obs["farms"][0]["money"] = 2000
        state = v021_d_module.GameState(obs)
        econ = v021_d_module.EconomicCalculator(state)
        strategy = v021_d_module.StrategicPlanner(state, econ)
        self.assertEqual(strategy.get_daily_plant_cap(20), 4, "Plant cap must be 4 during Stage 1")

    def test_stage_2_dynamic_plant_cap_scales_to_10(self):
        obs = dict(self.raw_obs)
        obs["day"] = 12
        obs["farms"][0]["money"] = 15000
        state = v021_d_module.GameState(obs)
        econ = v021_d_module.EconomicCalculator(state)
        strategy = v021_d_module.StrategicPlanner(state, econ)
        self.assertEqual(strategy.get_daily_plant_cap(20), 10, "Plant cap must scale to 10 on Day 12 with $15k liquidity and 20 empty tiles")

    def test_workload_driven_labor_scaling(self):
        # 55 crops on farm on Day 13 -> should hire 3 workers
        tiles = [[None]*10 for _ in range(10)]
        for y in range(5):
            for x in range(10):
                tiles[y][x] = {"kind": "PLANT", "crop": "STRAWBERRY", "planted_day": 11, "watered_today": False, "yield_units": 0}
        tiles[5][0] = {"kind": "PLANT", "crop": "STRAWBERRY", "planted_day": 11, "watered_today": False, "yield_units": 0}
        
        obs = dict(self.raw_obs)
        obs["day"] = 13
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 10000
        obs["farms"][0]["hands"] = []
        obs["farms"][0]["hires_today"] = 0
        
        state = v021_d_module.GameState(obs)
        econ = v021_d_module.EconomicCalculator(state)
        strategy = v021_d_module.StrategicPlanner(state, econ)
        planner = v021_d_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        allocator = v021_d_module.TaskAllocator(state, econ, tasks, strategy)
        allocator.allocate()
        
        hire_tasks = [t for t in tasks if t.action_type == "HIRE"]
        self.assertEqual(len(hire_tasks), 1, "Should hire additional worker when active crops exceed 50")

    def test_gated_land_expansion(self):
        # 1. Day 12, $15k cash, but 20 empty tiles in NW quadrant -> DO NOT BUY LAND (utilize existing land first)
        obs = dict(self.raw_obs)
        obs["day"] = 12
        obs["farms"][0]["money"] = 15000
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        tiles = [["LOCKED"]*10 for _ in range(10)]
        for r in range(5):
            for c in range(5):
                tiles[r][c] = None
        # Only 5 crops planted in NW, 20 empty
        for i in range(5):
            tiles[0][i] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": True, "yield_units": 0}
        obs["farms"][0]["tiles"] = tiles
        
        state = v021_d_module.GameState(obs)
        econ = v021_d_module.EconomicCalculator(state)
        strategy = v021_d_module.StrategicPlanner(state, econ)
        planner = v021_d_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(land_tasks), 0, "Must not buy land when 20 empty tiles remain")

        # 2. 22 crops planted in NW (3 empty tiles) -> BUY LAND
        for i in range(5, 22):
            r = i // 5
            c = i % 5
            tiles[r][c] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": True, "yield_units": 0}
            
        state = v021_d_module.GameState(obs)
        econ = v021_d_module.EconomicCalculator(state)
        strategy = v021_d_module.StrategicPlanner(state, econ)
        planner = v021_d_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(land_tasks), 1, "Must buy land when empty tiles <= 5 and cash is protected")

    def test_smoke_5_turns(self):
        agent_fn = v021_d_module.agent
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent_fn(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
