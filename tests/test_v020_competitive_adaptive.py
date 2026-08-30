import unittest
import importlib.util
from kaggle_environments import make

spec = importlib.util.spec_from_file_location("v020_b_agent", "agents/v020_b_competitive_adaptive.py")
v020_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v020_module)

GameState = v020_module.GameState
EconomicCalculator = v020_module.EconomicCalculator
StrategicPlanner = v020_module.StrategicPlanner
DailyPlanner = v020_module.DailyPlanner
agent = v020_module.agent

class TestV020CompetitiveAdaptive(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        self.raw_obs = self.env.state[0].observation
        
    def test_melon_selection_days_0_to_18(self):
        obs = dict(self.raw_obs)
        obs["day"] = 5
        state = GameState(obs)
        econ = EconomicCalculator(state)
        planner = StrategicPlanner(state, econ)
        evals = planner.evaluate_target_crops()
        self.assertIn("MELON", evals)
        self.assertGreater(evals["MELON"]["net_profit"], 0)
        
    def test_carrot_transition_days_19_to_25(self):
        obs = dict(self.raw_obs)
        obs["day"] = 20
        state = GameState(obs)
        econ = EconomicCalculator(state)
        planner = StrategicPlanner(state, econ)
        evals = planner.evaluate_target_crops()
        self.assertNotIn("MELON", evals) # Melon requires 10 days, only 9 left
        self.assertIn("CARROT", evals)
        
    def test_late_season_lifecycle(self):
        obs = dict(self.raw_obs)
        obs["day"] = 28 # Only 2 days left (days 28 and 29)
        state = GameState(obs)
        econ = EconomicCalculator(state)
        planner = StrategicPlanner(state, econ)
        evals = planner.evaluate_target_crops()
        self.assertEqual(len(evals), 0) # No crops can complete in 1 day
        
    def test_endgame_freeze_days_28_to_29(self):
        obs = dict(self.raw_obs)
        obs["day"] = 29
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strat = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strat)
        tasks = planner.plan_tasks()
        buy_seed_tasks = [t for t in tasks if t.action_type == "BUY_SEED"]
        self.assertEqual(len(buy_seed_tasks), 0)
        
    def test_smoke_5_turns(self):
        for _ in range(5):
            obs = self.env.state[0].observation
            act = agent(obs)
            self.assertIn("farmer", act)
            self.assertIn("hands", act)
            self.assertIn("market", act)
            self.env.step([act, "random"])

if __name__ == "__main__":
    unittest.main()
