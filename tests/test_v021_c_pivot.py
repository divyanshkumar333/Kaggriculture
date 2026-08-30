import unittest
import importlib.util
from kaggle_environments import make

spec_c = importlib.util.spec_from_file_location("v020_c_agent", "agents/v020_c_competitive_surgical.py")
v020_c_module = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(v020_c_module)

spec_v21c = importlib.util.spec_from_file_location("v021_c_agent", "agents/v021_c_two_stage_pivot.py")
v021_c_module = importlib.util.module_from_spec(spec_v21c)
spec_v21c.loader.exec_module(v021_c_module)

class TestV021CPivot(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation

    def test_stage_1_isolation_no_animals_early(self):
        # Day 3, $2000 cash -> Must NOT build pasture or buy animal in Stage 1
        obs = dict(self.raw_obs)
        obs["day"] = 3
        obs["hour"] = 0
        obs["farms"][0]["money"] = 2000
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        
        state = v021_c_module.GameState(obs)
        econ = v021_c_module.EconomicCalculator(state)
        strategy = v021_c_module.StrategicPlanner(state, econ)
        self.assertFalse(strategy.is_in_stage_2(), "Stage 1 must be active on Day 3")
        
        planner = v021_c_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        pasture_tasks = [t for t in tasks if t.action_type in ["BUILD_PASTURE", "BUILD_COOP", "BUY_ANIMAL"]]
        self.assertEqual(len(pasture_tasks), 0, "No livestock tasks allowed during Stage 1")
        
        # Melon seed buy should be active
        melon_buys = [t for t in tasks if t.action_type == "BUY_SEED" and t.kwargs.get("product") == "MELON"]
        self.assertEqual(len(melon_buys), 1, "Should plant Melons in Stage 1")

    def test_stage_2_liquidity_trigger(self):
        # Day 11, $14,000 cash (Melons sold) -> Stage 2 triggered!
        obs = dict(self.raw_obs)
        obs["day"] = 11
        obs["hour"] = 0
        obs["farms"][0]["money"] = 14000
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        
        state = v021_c_module.GameState(obs)
        econ = v021_c_module.EconomicCalculator(state)
        strategy = v021_c_module.StrategicPlanner(state, econ)
        self.assertTrue(strategy.is_in_stage_2(), "Stage 2 must trigger when liquidity exceeds $6,000 on Day 11")
        
        planner = v021_c_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        # Should queue BUY_LAND task
        land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(land_tasks), 1, "Should buy land upon Stage 2 liquidity surge")
        
        # Should queue BUILD_PASTURE task
        pasture_tasks = [t for t in tasks if t.action_type == "BUILD_PASTURE"]
        self.assertGreater(len(pasture_tasks), 0, "Should build pasture in Stage 2")

    def test_emergency_feed_safety_guard(self):
        # 4 Cows, 0 Wheat in shed -> BUY_PRODUCT WHEAT triggered
        tiles = [[None]*10 for _ in range(10)]
        tiles[0][0] = {"kind": "PASTURE", "animal": "COW", "fed_today": False}
        tiles[0][1] = {"kind": "PASTURE", "animal": "COW", "fed_today": False}
        obs = dict(self.raw_obs)
        obs["day"] = 12
        obs["hour"] = 0
        obs["farms"][0]["tiles"] = tiles
        obs["farms"][0]["money"] = 8000
        obs["farms"][0]["unlocked_quadrants"] = ["NW", "NE"]
        obs["private"]["shed"] = {"WHEAT": 0}
        
        state = v021_c_module.GameState(obs)
        econ = v021_c_module.EconomicCalculator(state)
        strategy = v021_c_module.StrategicPlanner(state, econ)
        planner = v021_c_module.DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        feed_buys = [t for t in tasks if t.action_type == "BUY_PRODUCT" and t.kwargs.get("product") == "WHEAT"]
        self.assertEqual(len(feed_buys), 1, "Emergency wheat buy must trigger when feed in shed is 0")

    def test_market_order_priority(self):
        obs = dict(self.raw_obs)
        obs["day"] = 12
        obs["hour"] = 2
        obs["farms"][0]["money"] = 8000
        obs["market"]["prices"] = {"MILK": 200, "WHEAT": 25, "STRAWBERRY": 120}
        
        state = v021_c_module.GameState(obs)
        econ = v021_c_module.EconomicCalculator(state)
        executor = v021_c_module.ActionExecutor(state, econ)
        
        tasks = [
            v021_c_module.Task("SELL", 5, kwargs={"product": "WHEAT", "quantity": 5}),
            v021_c_module.Task("SELL", 5, kwargs={"product": "MILK", "quantity": 5}),
            v021_c_module.Task("SELL", 5, kwargs={"product": "STRAWBERRY", "quantity": 5}),
            v021_c_module.Task("HIRE", 1),
        ]
        actions = executor.execute(tasks, {})
        market_actions = actions["market"]
        
        self.assertEqual(market_actions[0], ["HIRE"])
        milk_idx = [i for i, a in enumerate(market_actions) if a[0] == "SELL" and a[1] == "MILK"][0]
        wheat_idx = [i for i, a in enumerate(market_actions) if a[0] == "SELL" and a[1] == "WHEAT"][0]
        self.assertLess(milk_idx, wheat_idx, "Milk sale must execute before Wheat sale")

    def test_smoke_5_turns(self):
        agent_fn = v021_c_module.agent
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent_fn(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
