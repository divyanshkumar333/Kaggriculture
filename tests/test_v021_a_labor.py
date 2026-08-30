import unittest
import importlib.util
from kaggle_environments import make

spec_c = importlib.util.spec_from_file_location("v020_c_agent", "agents/v020_c_competitive_surgical.py")
v020_c_module = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(v020_c_module)

spec_v21 = importlib.util.spec_from_file_location("v021_a_agent", "agents/v021_a_labor_throughput.py")
v021_a_module = importlib.util.module_from_spec(spec_v21)
spec_v21.loader.exec_module(v021_a_module)

class TestV021ALabor(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation

    def test_dynamic_plant_cap_scaling(self):
        self.assertEqual(v021_a_module.get_daily_plant_cap(1), 4)
        self.assertEqual(v021_a_module.get_daily_plant_cap(2), 6)
        self.assertEqual(v021_a_module.get_daily_plant_cap(3), 8)
        self.assertEqual(v021_a_module.get_daily_plant_cap(4), 10)

    def test_market_order_priority_reordering(self):
        obs = dict(self.raw_obs)
        obs["day"] = 4
        obs["hour"] = 4
        obs["farms"][0]["money"] = 5000
        obs["market"]["prices"] = {"MELON": 250, "WHEAT": 25, "STRAWBERRY": 120, "CARROT": 35}
        obs["private"]["shed"] = {"WHEAT": 5, "MELON": 5, "STRAWBERRY": 5, "CARROT": 5}
        
        state = v021_a_module.GameState(obs)
        econ = v021_a_module.EconomicCalculator(state)
        executor = v021_a_module.ActionExecutor(state, econ)
        
        tasks = [
            v021_a_module.Task("SELL", 5, kwargs={"product": "WHEAT", "quantity": 5}),
            v021_a_module.Task("SELL", 5, kwargs={"product": "MELON", "quantity": 5}),
            v021_a_module.Task("SELL", 5, kwargs={"product": "CARROT", "quantity": 5}),
            v021_a_module.Task("SELL", 5, kwargs={"product": "STRAWBERRY", "quantity": 5}),
            v021_a_module.Task("HIRE", 1),
        ]
        actions = executor.execute(tasks, {})
        market_actions = actions["market"]
        
        # HIRE must be first
        self.assertEqual(market_actions[0], ["HIRE"])
        # MELON ($250 * 5 = 1250) must come before WHEAT ($25 * 5 = 125)
        melon_idx = -1
        wheat_idx = -1
        for idx, act in enumerate(market_actions):
            if act[0] == "SELL" and act[1] == "MELON":
                melon_idx = idx
            elif act[0] == "SELL" and act[1] == "WHEAT":
                wheat_idx = idx
                
        self.assertTrue(melon_idx != -1 and wheat_idx != -1)
        self.assertLess(melon_idx, wheat_idx, "Melon sale should execute before Wheat sale")

    def test_labor_scaling_under_workload(self):
        # Construct state with 50 unwatered plants (100 actions needed vs 72 available from 3 workers)
        tiles = [[None]*10 for _ in range(10)]
        for y in range(5):
            for x in range(10):
                tiles[y][x] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": False, "yield_units": 0}
                
        obs = dict(self.raw_obs)
        obs["day"] = 1
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 3000
        obs["farms"][0]["farmer"] = [0, 0]
        obs["farms"][0]["hands"] = [[0, 1], [0, 2]]
        obs["farms"][0]["hires_today"] = 2
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        
        state = v021_a_module.GameState(obs)
        econ = v021_a_module.EconomicCalculator(state)
        strategy = v021_a_module.StrategicPlanner(state, econ)
        planner = v021_a_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        allocator = v021_a_module.TaskAllocator(state, econ, tasks, strategy)
        allocator.allocate()
        
        hire_tasks = [t for t in tasks if t.action_type == "HIRE"]
        self.assertGreater(len(hire_tasks), 0, "Should hire additional workers when 30 unwatered crops create deficit")

    def test_hiring_protects_operating_reserve(self):
        tiles = [[None]*10 for _ in range(10)]
        for y in range(2):
            for x in range(10):
                tiles[y][x] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": False, "yield_units": 0}
                
        obs = dict(self.raw_obs)
        obs["day"] = 1
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 100
        obs["farms"][0]["farmer"] = [0, 0]
        obs["farms"][0]["hands"] = []
        obs["farms"][0]["hires_today"] = 0
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        
        state = v021_a_module.GameState(obs)
        econ = v021_a_module.EconomicCalculator(state)
        strategy = v021_a_module.StrategicPlanner(state, econ)
        planner = v021_a_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        allocator = v021_a_module.TaskAllocator(state, econ, tasks, strategy)
        allocator.allocate()
        
        hire_tasks = [t for t in tasks if t.action_type == "HIRE"]
        self.assertEqual(len(hire_tasks), 0, "Should block hiring when money is below operating reserve")

    def test_smoke_5_turns(self):
        agent_fn = v021_a_module.agent
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent_fn(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
