import unittest
import importlib.util
from kaggle_environments import make

spec_c = importlib.util.spec_from_file_location("v020_c_agent", "agents/v020_c_competitive_surgical.py")
v020_c_module = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(v020_c_module)

spec_v21b = importlib.util.spec_from_file_location("v021_b_agent", "agents/v021_b_industrial_livestock.py")
v021_b_module = importlib.util.module_from_spec(spec_v21b)
spec_v21b.loader.exec_module(v021_b_module)

class TestV021BLivestock(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation

    def test_pasture_and_animal_purchases_when_cash_allows(self):
        # Setup: Day 3, $3000 cash, 1 empty pasture tile
        tiles = [[None]*10 for _ in range(10)]
        tiles[0][0] = {"kind": "PASTURE"} # empty pasture
        obs = dict(self.raw_obs)
        obs["day"] = 3
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 3000
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        
        state = v021_b_module.GameState(obs)
        econ = v021_b_module.EconomicCalculator(state)
        strategy = v021_b_module.StrategicPlanner(state, econ)
        planner = v021_b_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        # Should queue BUY_ANIMAL COW task
        animal_tasks = [t for t in tasks if t.action_type == "BUY_ANIMAL" and t.kwargs.get("product") == "COW"]
        self.assertEqual(len(animal_tasks), 1, "Should purchase Cow for empty pasture when funds allow")

    def test_late_season_animal_purchases_rejected(self):
        # Setup: Day 25 (only 5 days left < 8.5 day payback): Animal purchases rejected
        tiles = [[None]*10 for _ in range(10)]
        tiles[0][0] = {"kind": "PASTURE"}
        obs = dict(self.raw_obs)
        obs["day"] = 25
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 5000
        
        state = v021_b_module.GameState(obs)
        econ = v021_b_module.EconomicCalculator(state)
        strategy = v021_b_module.StrategicPlanner(state, econ)
        planner = v021_b_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        animal_tasks = [t for t in tasks if t.action_type == "BUY_ANIMAL"]
        self.assertEqual(len(animal_tasks), 0, "Should reject animal purchases late in season")

    def test_feed_safety_guard_buys_wheat_when_low(self):
        # Setup: 2 Cows on farm, 0 wheat in shed -> should queue BUY_PRODUCT WHEAT
        tiles = [[None]*10 for _ in range(10)]
        tiles[0][0] = {"kind": "PASTURE", "animal": "COW", "fed_today": False}
        tiles[0][1] = {"kind": "PASTURE", "animal": "COW", "fed_today": False}
        obs = dict(self.raw_obs)
        obs["day"] = 5
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 2000
        obs["private"]["shed"] = {"WHEAT": 0}
        
        state = v021_b_module.GameState(obs)
        econ = v021_b_module.EconomicCalculator(state)
        strategy = v021_b_module.StrategicPlanner(state, econ)
        planner = v021_b_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        buy_product_tasks = [t for t in tasks if t.action_type == "BUY_PRODUCT" and t.kwargs.get("product") == "WHEAT"]
        self.assertEqual(len(buy_product_tasks), 1, "Should trigger emergency wheat buy when feed reserve is 0")

    def test_market_execution_priority_milk_before_wheat(self):
        obs = dict(self.raw_obs)
        obs["day"] = 5
        obs["hour"] = 2
        obs["farms"][0]["money"] = 5000
        obs["market"]["prices"] = {"MILK": 200, "WHEAT": 25, "WOOL": 250}
        
        state = v021_b_module.GameState(obs)
        econ = v021_b_module.EconomicCalculator(state)
        executor = v021_b_module.ActionExecutor(state, econ)
        
        tasks = [
            v021_b_module.Task("SELL", 5, kwargs={"product": "WHEAT", "quantity": 5}),
            v021_b_module.Task("SELL", 5, kwargs={"product": "MILK", "quantity": 3}),
            v021_b_module.Task("SELL", 5, kwargs={"product": "WOOL", "quantity": 2}),
            v021_b_module.Task("HIRE", 1),
        ]
        actions = executor.execute(tasks, {})
        market_actions = actions["market"]
        
        # HIRE must be first
        self.assertEqual(market_actions[0], ["HIRE"])
        # MILK ($200*3 = 600) and WOOL ($250*2 = 500) must execute before WHEAT ($25*5 = 125)
        milk_idx = -1
        wheat_idx = -1
        for idx, act in enumerate(market_actions):
            if act[0] == "SELL" and act[1] == "MILK": milk_idx = idx
            elif act[0] == "SELL" and act[1] == "WHEAT": wheat_idx = idx
            
        self.assertTrue(milk_idx != -1 and wheat_idx != -1)
        self.assertLess(milk_idx, wheat_idx, "Milk sale should execute before Wheat sale")

    def test_smoke_5_turns(self):
        agent_fn = v021_b_module.agent
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent_fn(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
