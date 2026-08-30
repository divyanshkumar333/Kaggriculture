import unittest
import importlib.util
from kaggle_environments import make

# Load V020-C
spec_c = importlib.util.spec_from_file_location("v020_c_agent", "agents/v020_c_competitive_surgical.py")
v020_c_module = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(v020_c_module)

# Load V020-A Control for comparative unit testing
spec_a = importlib.util.spec_from_file_location("v020_a_agent", "agents/v020_a_control.py")
v020_a_module = importlib.util.module_from_spec(spec_a)
spec_a.loader.exec_module(v020_a_module)

class TestV020CSurgical(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation

    def test_fractional_seed_stall_reproduction_and_fix(self):
        # Setup: Farmer has 1 MELON seed in inventory and $2000 cash, 10 empty tiles
        obs = dict(self.raw_obs)
        obs["day"] = 5
        obs["farms"][0]["money"] = 2000
        obs["private"]["seeds"] = {"MELON": 1}
        
        # Test V020-A (Old Control): reproduces the bug (buys 0 seeds because seeds.get("MELON") != 0)
        state_a = v020_a_module.GameState(obs)
        econ_a = v020_a_module.EconomicCalculator(state_a)
        strat_a = v020_a_module.StrategicPlanner(state_a, econ_a)
        planner_a = v020_a_module.DailyPlanner(state_a, econ_a, strat_a)
        tasks_a = planner_a.plan_tasks()
        buy_tasks_a = [t for t in tasks_a if t.action_type == "BUY_SEED" and t.kwargs.get("product") == "MELON"]
        self.assertEqual(len(buy_tasks_a), 0, "Old V020-A failed to buy seeds when 1 seed was in inventory (Bug reproduced)")

        # Test V020-C (Fixed): buys 3 seeds to restore inventory to batch cap of 4
        state_c = v020_c_module.GameState(obs)
        econ_c = v020_c_module.EconomicCalculator(state_c)
        strat_c = v020_c_module.StrategicPlanner(state_c, econ_c)
        planner_c = v020_c_module.DailyPlanner(state_c, econ_c, strat_c)
        tasks_c = planner_c.plan_tasks()
        buy_tasks_c = [t for t in tasks_c if t.action_type == "BUY_SEED" and t.kwargs.get("product") == "MELON"]
        self.assertEqual(len(buy_tasks_c), 1, "V020-C should generate BUY_SEED task")
        self.assertEqual(buy_tasks_c[0].kwargs.get("quantity"), 3, "V020-C should buy 3 seeds to restore batch cap to 4")

    def test_endgame_purchase_timing(self):
        # 1. Early season (Day 5): Normal Melon purchase
        obs = dict(self.raw_obs)
        obs["day"] = 5
        obs["farms"][0]["money"] = 2000
        obs["private"]["seeds"] = {"MELON": 0}
        state = v020_c_module.GameState(obs)
        econ = v020_c_module.EconomicCalculator(state)
        strat = v020_c_module.StrategicPlanner(state, econ)
        planner = v020_c_module.DailyPlanner(state, econ, strat)
        tasks = planner.plan_tasks()
        melon_buys = [t for t in tasks if t.action_type == "BUY_SEED" and t.kwargs.get("product") == "MELON"]
        self.assertEqual(len(melon_buys), 1)

        # 2. One day too late for Melon (Day 20): Melon requires 10 days, 30-20=10 days left (remaining_days-1 = 9 < 10)
        obs["day"] = 20
        state = v020_c_module.GameState(obs)
        econ = v020_c_module.EconomicCalculator(state)
        strat = v020_c_module.StrategicPlanner(state, econ)
        planner = v020_c_module.DailyPlanner(state, econ, strat)
        tasks = planner.plan_tasks()
        melon_buys = [t for t in tasks if t.action_type == "BUY_SEED" and t.kwargs.get("product") == "MELON"]
        self.assertEqual(len(melon_buys), 0, "Melon purchases must be rejected on Day 20")

    def test_land_expansion_reserve(self):
        # 1. Insufficient cash for land ($1,200 < $1,000 + $720 reserve): No expansion
        obs = dict(self.raw_obs)
        obs["day"] = 12
        obs["farms"][0]["money"] = 1200
        obs["farms"][0]["unlocked_quadrants"] = ["NW"]
        # Fill 20 tiles, leave 5 empty
        tiles = obs["farms"][0]["tiles"]
        count = 0
        for r in range(5):
            for c in range(5):
                if count < 20:
                    tiles[r][c] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": True, "yield_units": 0}
                count += 1
                
        state = v020_c_module.GameState(obs)
        econ = v020_c_module.EconomicCalculator(state)
        strat = v020_c_module.StrategicPlanner(state, econ)
        planner = v020_c_module.DailyPlanner(state, econ, strat)
        tasks = planner.plan_tasks()
        land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(land_tasks), 0, "Should not buy land when cash < land_price + operating_reserve")

        # 2. Sufficient cash ($1,850 > $1,000 + $720 reserve) and capacity constrained: Expands land!
        obs["farms"][0]["money"] = 1850
        state = v020_c_module.GameState(obs)
        econ = v020_c_module.EconomicCalculator(state)
        strat = v020_c_module.StrategicPlanner(state, econ)
        planner = v020_c_module.DailyPlanner(state, econ, strat)
        tasks = planner.plan_tasks()
        land_tasks = [t for t in tasks if t.action_type == "BUY_LAND"]
        self.assertEqual(len(land_tasks), 1, "Should buy land when cash >= land_price + operating_reserve")

    def test_smoke_5_turns(self):
        agent_fn = v020_c_module.agent
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent_fn(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
