import unittest
import copy
from agents import v028_market_c

# We will test the full middleware wrapper
# by mocking the base V027 agent so it returns exactly what we specify,
# then verifying the middleware mutates it correctly and DOES NOT CRASH.

class TestMarketMiddleware(unittest.TestCase):

    def setUp(self):
        # We replace the base agent with a mock that returns self.mock_action
        self.mock_action = {"farmer": ["PASS"], "hands": [], "market": []}
        
        # Patch the base agent inside the module
        self.original_v027_agent = v028_market_c.v027_agent
        v028_market_c.v027_agent = lambda obs: copy.deepcopy(self.mock_action)
        
        # Default dict-based obs
        self.obs = {
            "player": 0, "step": 1, "day": 1, "hour": 1,
            "farms": [
                {"money": 3000, "tiles": [[None]*10]*10, "farmer": [0,0], "hands": [], "unlocked_quadrants": ["NW"], "hires_today": 0},
                {"money": 3000, "tiles": [[None]*10]*10, "farmer": [0,0], "hands": [], "unlocked_quadrants": ["NW"], "hires_today": 0}
            ],
            "private": {
                "shed": {},
                "seeds": {},
                "inventories": [[None]*10]
            },
            "market": {
                "inventory": {"WHEAT": 10000, "STRAWBERRY": 10000},
                "prices": {"WHEAT": 25, "STRAWBERRY": 120}
            },
            "town": {
                "unlocked_shops": []
            }
        }
        self.conf = {"turnsPerDay": 24, "townShopSellInterval": 4, "townCenterSellInterval": 24}

    def tearDown(self):
        v028_market_c.v027_agent = self.original_v027_agent

    def test_zero_sell_orders(self):
        self.mock_action["market"] = [["BUY_SEED", "WHEAT", 1], ["HIRE"]]
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(len(res["market"]), 2)
        self.assertEqual(res["market"][0][0], "BUY_SEED")

    def test_one_sell_order(self):
        self.mock_action["market"] = [["SELL", "WHEAT", 10]]
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(len(res["market"]), 1)
        self.assertEqual(res["market"][0], ["SELL", "WHEAT", 10])

    def test_multiple_sell_orders(self):
        # STRAWBERRY has higher impact per unit than WHEAT
        self.mock_action["market"] = [["SELL", "WHEAT", 10], ["SELL", "STRAWBERRY", 10]]
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(len(res["market"]), 2)
        # Strawberry should sort first!
        self.assertEqual(res["market"][0][1], "STRAWBERRY")
        self.assertEqual(res["market"][1][1], "WHEAT")

    def test_mixed_buy_sell(self):
        self.mock_action["market"] = [["SELL", "WHEAT", 10], ["BUY_SEED", "WHEAT", 5], ["SELL", "STRAWBERRY", 10]]
        res = v028_market_c.agent(self.obs, self.conf)
        # Should keep the BUY_SEED in place or interspersed, but Strawberry should be before Wheat
        sells = [o for o in res["market"] if o[0] == "SELL"]
        self.assertEqual(sells[0][1], "STRAWBERRY")
        self.assertEqual(sells[1][1], "WHEAT")
        buys = [o for o in res["market"] if o[0] != "SELL"]
        self.assertEqual(len(buys), 1)

    def test_empty_market_list(self):
        self.mock_action["market"] = []
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(res["market"], [])
        
    def test_missing_market_fields(self):
        # Remove inventory and prices completely
        del self.obs["market"]
        self.mock_action["market"] = [["SELL", "WHEAT", 10], ["SELL", "STRAWBERRY", 10]]
        # Should not crash, and should still calculate based on defaults (10000 inventory)
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(len(res["market"]), 2)

    def test_inventory_equilibrium_conditions(self):
        for w_inv, s_inv in [(9000, 9000), (10000, 10000), (12000, 12000)]:
            self.obs["market"] = {"inventory": {"WHEAT": w_inv, "STRAWBERRY": s_inv}, "prices": {}}
            self.mock_action["market"] = [["SELL", "WHEAT", 10], ["SELL", "STRAWBERRY", 10]]
            res = v028_market_c.agent(self.obs, self.conf)
            self.assertEqual(len(res["market"]), 2)
            
    def test_quantity_edge_cases(self):
        self.mock_action["market"] = [["SELL", "WHEAT", 0], ["SELL", "STRAWBERRY", 99999]]
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(len(res["market"]), 2)

    def test_all_dynamic_game_hours(self):
        for hour in range(24):
            self.obs["hour"] = hour
            self.mock_action["market"] = [["SELL", "WHEAT", 10], ["SELL", "STRAWBERRY", 10]]
            res = v028_market_c.agent(self.obs, self.conf)
            self.assertEqual(len(res["market"]), 2)

    def test_premium_market_lead_activation(self):
        # Strawberry is premium. 
        # Demand is 0 if no shops unlocked, but town center wants it every 24 turns (demand = 1 per day).
        # Wait, center demand is 1 per day. So demand is NEVER 0 unless configured differently?
        # Let's test with a massive config that makes center interval HUGE.
        self.conf["townCenterSellInterval"] = 9999999
        self.obs["private"]["shed"] = {"STRAWBERRY": 50}
        self.mock_action["market"] = [["SELL", "STRAWBERRY", 4]]  # Base agent sells 4
        
        # Town demand is practically 0
        res = v028_market_c.agent(self.obs, self.conf)
        # Should pull forward the whole shed!
        sells = [o for o in res["market"] if o[0] == "SELL"]
        self.assertEqual(sells[0][2], 50)
        
    def test_preserves_other_actions(self):
        self.mock_action["farmer"] = ["NORTH"]
        self.mock_action["hands"] = [["WATER"]]
        res = v028_market_c.agent(self.obs, self.conf)
        self.assertEqual(res["farmer"], ["NORTH"])
        self.assertEqual(res["hands"], [["WATER"]])
        
    def test_100_hand_constructed_states(self):
        import random
        random.seed(42)
        # Run 100 random variations to ensure no crashes
        for i in range(100):
            obs_copy = copy.deepcopy(self.obs)
            obs_copy["hour"] = random.randint(0, 23)
            obs_copy["market"]["inventory"]["WHEAT"] = random.randint(0, 20000)
            obs_copy["market"]["inventory"]["STRAWBERRY"] = random.randint(0, 20000)
            obs_copy["private"]["shed"]["WHEAT"] = random.randint(0, 100)
            
            # Random malformed stuff
            if i % 10 == 0:
                obs_copy["market"] = None
            if i % 11 == 0:
                obs_copy["town"] = None
                
            self.mock_action["market"] = [
                ["SELL", "WHEAT", random.randint(0, 100)],
                ["SELL", "STRAWBERRY", random.randint(0, 100)],
                ["SELL", "INVALID", 10],
                ["BUY_SEED", "CARROT", 2]
            ]
            
            try:
                res = v028_market_c.agent(obs_copy, self.conf)
                self.assertIsNotNone(res)
            except Exception as e:
                self.fail(f"Crashed on iteration {i}: {e}")

if __name__ == '__main__':
    unittest.main()
