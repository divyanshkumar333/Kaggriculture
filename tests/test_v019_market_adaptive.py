import os
import sys
# Ensure current working directory is first in sys.path
sys.path.insert(0, os.path.abspath("."))

import unittest
import importlib.util

def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v19_b = load_module_from_file("v019_b", "agents/v019_b_market_adaptive.py")
v19_a = load_module_from_file("v019_a", "agents/v019_a_control.py")

GameState = v19_b.GameState
EconomicCalculator = v19_b.EconomicCalculator
DailyPlanner = v19_b.DailyPlanner
StrategicPlanner = v19_b.StrategicPlanner
StrategyConfig = v19_b.StrategyConfig
agent_b = v19_b.agent
agent_a = v19_a.agent

from kaggle_environments import make

def make_mock_obs(day=0, hour=0, money=3000, market_inv=None, unlocked_shops=None, my_tiles=None, opp_tiles=None, seeds=None, shed=None):
    if market_inv is None:
        market_inv = {"WHEAT": 10000, "CARROT": 10000, "TOMATO": 10000, "STRAWBERRY": 10000, "MELON": 10000}
    if unlocked_shops is None:
        unlocked_shops = []
    if my_tiles is None:
        my_tiles = [[None for _ in range(10)] for _ in range(10)]
    if opp_tiles is None:
        opp_tiles = [[None for _ in range(10)] for _ in range(10)]
    if seeds is None:
        seeds = {}
    if shed is None:
        shed = {}
        
    return {
        "player": 0,
        "step": day * 24 + hour,
        "day": day,
        "hour": hour,
        "farms": [
            {
                "money": money,
                "tiles": my_tiles,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0
            },
            {
                "money": money,
                "tiles": opp_tiles,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0
            }
        ],
        "market": {
            "inventory": market_inv,
            "prices": {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250}
        },
        "town": {
            "unlocked_shops": unlocked_shops
        },
        "private": {
            "seeds": seeds,
            "shed": shed,
            "inventories": [{}]
        }
    }

class TestV019MarketAdaptive(unittest.TestCase):

    def test_a_healthy_melon_market(self):
        """A. Healthy Melon market -> Melon should be selected as optimal."""
        obs = make_mock_obs(day=0, market_inv={"MELON": 10000, "CARROT": 10000, "WHEAT": 10000})
        state = GameState(obs)
        econ = EconomicCalculator(state)
        evals = econ.evaluate_competitive_crops()
        
        self.assertTrue(evals["MELON"]["feasible"])
        self.assertGreater(evals["MELON"]["profit_per_action"], evals["CARROT"]["profit_per_action"])
        self.assertGreater(evals["MELON"]["profit_per_action"], evals["WHEAT"]["profit_per_action"])

    def test_b_saturated_melon_market(self):
        """B. Saturated Melon market -> Should select a profitable alternative like Carrot or Tomato."""
        obs = make_mock_obs(day=5, market_inv={"MELON": 10400, "CARROT": 10000, "TOMATO": 10000, "WHEAT": 10000})
        state = GameState(obs)
        econ = EconomicCalculator(state)
        evals = econ.evaluate_competitive_crops()
        
        self.assertLess(evals["MELON"]["net_profit"], 0) # Saturated melon loses money
        self.assertGreater(evals["CARROT"]["profit_per_action"], evals["MELON"]["profit_per_action"])
        self.assertGreater(evals["CARROT"]["net_profit"], 0)

    def test_c_late_season_impossible_to_mature(self):
        """C. Reject crops that cannot mature in remaining days."""
        obs = make_mock_obs(day=23)
        state = GameState(obs)
        econ = EconomicCalculator(state)
        evals = econ.evaluate_competitive_crops()
        
        self.assertFalse(evals["MELON"]["feasible"])
        self.assertEqual(evals["MELON"]["achievable_yield"], 0)
        self.assertTrue(evals["CARROT"]["feasible"])
        self.assertGreater(evals["CARROT"]["achievable_yield"], 0)

    def test_d_opponent_pipeline_awareness(self):
        """D. Account for opponent's planted pipeline crashing the market."""
        opp_tiles = [[None for _ in range(10)] for _ in range(10)]
        for i in range(20):
            opp_tiles[i // 5][i % 5] = {"kind": "PLANT", "crop": "MELON", "planted_day": 0, "watered_today": True, "yield_units": 0}
            
        obs = make_mock_obs(day=2, opp_tiles=opp_tiles, market_inv={"MELON": 10100})
        state = GameState(obs)
        econ = EconomicCalculator(state)
        evals = econ.evaluate_competitive_crops()
        
        self.assertGreaterEqual(evals["MELON"]["projected_inventory"], 10200)
        self.assertLess(evals["MELON"]["projected_unit_price"], 50)

    def test_e_melon_higher_marginal_roi_when_healthy(self):
        """E. Melon has higher marginal ROI -> stay with Melon."""
        obs = make_mock_obs(day=1, market_inv={"MELON": 9900, "CARROT": 10000})
        state = GameState(obs)
        evals = EconomicCalculator(state).evaluate_competitive_crops()
        self.assertGreater(evals["MELON"]["profit_per_action"], evals["CARROT"]["profit_per_action"])

    def test_f_market_recovery_allows_switch_back(self):
        """F. If market drains and recovers, Melon can be selected again."""
        obs_saturated = make_mock_obs(day=5, market_inv={"MELON": 10300})
        evals1 = EconomicCalculator(GameState(obs_saturated)).evaluate_competitive_crops()
        
        obs_recovered = make_mock_obs(day=5, market_inv={"MELON": 9900})
        evals2 = EconomicCalculator(GameState(obs_recovered)).evaluate_competitive_crops()
        
        self.assertGreater(evals2["MELON"]["profit_per_action"], evals1["MELON"]["profit_per_action"])
        self.assertGreater(evals2["MELON"]["profit_per_action"], evals2["CARROT"]["profit_per_action"])

    def test_g_late_season_crop_rejection(self):
        """G. Late season -> reject crops that cannot mature."""
        obs = make_mock_obs(day=28)
        evals = EconomicCalculator(GameState(obs)).evaluate_competitive_crops()
        self.assertFalse(evals["MELON"]["feasible"])
        self.assertFalse(evals["TOMATO"]["feasible"])
        self.assertFalse(evals["STRAWBERRY"]["feasible"])

    def test_h_batch_cap_preservation(self):
        """H. Daily plant cap (batch cap) is respected in DailyPlanner."""
        seeds = {"MELON": 10}
        obs = make_mock_obs(day=0, seeds=seeds)
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        plant_tasks = [t for t in tasks if t.action_type == "PLANT"]
        self.assertLessEqual(len(plant_tasks), 4)

    def test_i_smoke_full_match(self):
        """I & J. Full match smoke test between V019-B and V019-A."""
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
        env.run([agent_b, agent_a])
        final = env.steps[-1]
        self.assertIsNotNone(final[0].reward)
        self.assertIsNotNone(final[1].reward)
        self.assertNotEqual(final[0].status, "ERROR")
        self.assertNotEqual(final[1].status, "ERROR")

if __name__ == "__main__":
    unittest.main()
