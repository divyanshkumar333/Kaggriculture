import unittest
import os
import sys

# To allow importing agents
sys.path.append(os.path.abspath("."))

from agents.v004_b_diversify import DailyPlanner, GameState, EconomicCalculator, StrategicPlanner, MetricsTracker, Task

class MockGameState:
    def __init__(self, money, market_inv, seeds, shed, my_farm_tiles):
        self.money = money
        self.board_size = 10
        self.market = {"inventory": market_inv}
        self.seeds = seeds
        self.shed = shed
        self.my_farm = {"tiles": my_farm_tiles}
        self.day = 1
        self.hour = 0
        self.player = 0
        
class TestV004Diversify(unittest.TestCase):
    def setUp(self):
        os.environ["KAGGRICULTURE_SEED"] = "test_v004"
        # Reset metrics
        MetricsTracker.get()["workers"]["useful_actions"] = 0
        MetricsTracker.get()["farmer"]["useful_actions"] = 0
        MetricsTracker.get()["economy"]["worker_spending"] = 0
        for crop in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]:
            MetricsTracker.get()["crops"][crop]["planted"] = 0
            MetricsTracker.get()["crops"][crop]["deaths"] = 0

    def test_crop_selection_early_game(self):
        # Money 3000, market fresh (10000 all)
        market_inv = {c: 10000 for c in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]}
        tiles = [[None]*10 for _ in range(10)]
        state = MockGameState(3000, market_inv, {}, {}, tiles)
        
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        
        # MELON has highest base price ($250) and max yield (6). Expected revenue = $1500. Seed = $100.
        # STRAWBERRY has base ($120), max yield (16). Expected revenue = $1920. Seed = $200.
        # MELON takes 12 actions. STRAWBERRY takes 20 actions.
        # Labor cost = action * 0.04 (early game default).
        # MELON labor = 0.48. STRAWBERRY labor = 0.80.
        # MELON profit = 1500 - 100 - 0.48 = 1399.52. Per action = 116.6
        # STRAWBERRY profit = 1920 - 200 - 0.80 = 1719.2. Per action = 85.96
        # MELON should win early game!
        
        buy_tasks = [t for t in tasks if t.action_type == "BUY_SEED"]
        self.assertEqual(len(buy_tasks), 1)
        self.assertEqual(buy_tasks[0].kwargs["product"], "MELON")
        
    def test_crop_selection_melon_saturation(self):
        # Market saturated for MELON (inventory 10500) -> price drops significantly
        market_inv = {c: 10000 for c in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]}
        market_inv["MELON"] = 10500
        
        tiles = [[None]*10 for _ in range(10)]
        state = MockGameState(3000, market_inv, {}, {}, tiles)
        
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        
        # With MELON saturated, STRAWBERRY should become the most profitable per action
        buy_tasks = [t for t in tasks if t.action_type == "BUY_SEED"]
        self.assertEqual(len(buy_tasks), 1)
        self.assertNotEqual(buy_tasks[0].kwargs["product"], "MELON")

    def test_high_labor_cost_prefers_low_labor_crop(self):
        # Artificially inflate labor cost
        MetricsTracker.get()["workers"]["useful_actions"] = 10
        MetricsTracker.get()["economy"]["worker_spending"] = 2000 
        # cost per action = $200!
        
        market_inv = {c: 10000 for c in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]}
        tiles = [[None]*10 for _ in range(10)]
        state = MockGameState(3000, market_inv, {}, {}, tiles)
        
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        
        # STRAWBERRY takes 20 actions -> labor cost $4000 (negative profit)
        # MELON takes 12 actions -> labor cost $2400 (negative profit)
        # WHEAT takes 5 actions -> labor cost $1000 (revenue $150, still negative maybe?)
        # Let's see what it picks. It shouldn't buy anything if all profit_per_action < 0
        buy_tasks = [t for t in tasks if t.action_type == "BUY_SEED"]
        self.assertEqual(len(buy_tasks), 0)

if __name__ == '__main__':
    unittest.main()
