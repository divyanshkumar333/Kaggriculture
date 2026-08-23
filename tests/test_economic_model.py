import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from agents.v001_baseline import EconomicCalculator, MARKET_PARAMS as AGENT_MARKET_PARAMS

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS as ENV_MARKET_PARAMS,
    market_price as env_market_price,
    PRODUCTS,
    PRICE_FLOOR
)

# Mock GameState to test EconomicCalculator
class MockGameState:
    def __init__(self, market_inv=None):
        self.market = {"inventory": market_inv or {p: 10000 for p in PRODUCTS}}

class TestEconomicModel(unittest.TestCase):
    def setUp(self):
        self.state = MockGameState()
        self.econ = EconomicCalculator(self.state)

    def test_params_match(self):
        """Test that the agent's MARKET_PARAMS exactly match the environment's."""
        for product in PRODUCTS:
            self.assertIn(product, AGENT_MARKET_PARAMS)
            env_params = ENV_MARKET_PARAMS[product]
            agent_params = AGENT_MARKET_PARAMS[product]
            for key in env_params:
                self.assertEqual(env_params[key], agent_params[key], f"Mismatch in {product} {key}")

    def test_price_at_i0(self):
        """Test inventory exactly at I0."""
        for product in PRODUCTS:
            I0 = ENV_MARKET_PARAMS[product]["I0"]
            env_p = env_market_price(product, I0, ENV_MARKET_PARAMS)
            agent_p = self.econ.get_price_at_inventory(product, I0)
            self.assertEqual(env_p, agent_p, f"{product} price at I0")

    def test_price_below_i0(self):
        """Test inventory below I0 (scarcity)."""
        for product in PRODUCTS:
            I0 = ENV_MARKET_PARAMS[product]["I0"]
            T = ENV_MARKET_PARAMS[product]["T"]
            for offset in [1, 10, int(T/2), T, T*2]:
                inv = max(0, I0 - offset)
                env_p = env_market_price(product, inv, ENV_MARKET_PARAMS)
                agent_p = self.econ.get_price_at_inventory(product, inv)
                self.assertEqual(env_p, agent_p, f"{product} price at {inv}")

    def test_price_above_i0(self):
        """Test inventory above I0 (glut)."""
        for product in PRODUCTS:
            I0 = ENV_MARKET_PARAMS[product]["I0"]
            T = ENV_MARKET_PARAMS[product]["T"]
            for offset in [1, 10, int(T/2), T, T*2, T*5]:
                inv = I0 + offset
                env_p = env_market_price(product, inv, ENV_MARKET_PARAMS)
                agent_p = self.econ.get_price_at_inventory(product, inv)
                self.assertEqual(env_p, agent_p, f"{product} price at {inv}")

    def test_price_floor(self):
        """Test that price properly floors at $1."""
        for product in PRODUCTS:
            inv = 10000
            # For log shapes, it takes a HUGE inventory to reach floor.
            # We'll just calculate a large enough inventory directly, or use a step
            while env_market_price(product, inv, ENV_MARKET_PARAMS) > 1:
                if ENV_MARKET_PARAMS[product]["above_func"] == "log":
                    inv *= 2
                else:
                    inv += 10000
                    
            env_p = env_market_price(product, inv, ENV_MARKET_PARAMS)
            agent_p = self.econ.get_price_at_inventory(product, inv)
            self.assertEqual(env_p, 1) # verify environment floored it
            self.assertEqual(agent_p, PRICE_FLOOR)
            self.assertEqual(env_p, agent_p)

    def test_sequential_selling_and_large_orders(self):
        """Test expected_sell_value simulates sequential unit-by-unit selling accurately."""
        for product in PRODUCTS:
            I0 = ENV_MARKET_PARAMS[product]["I0"]
            T = ENV_MARKET_PARAMS[product]["T"]
            
            for qty in [1, 5, 25, 100]:
                self.state.market["inventory"][product] = I0
                agent_rev = self.econ.expected_sell_value(product, qty)
                
                # Simulate environment logic
                env_rev = 0
                env_inv = I0
                for _ in range(qty):
                    p = env_market_price(product, env_inv, ENV_MARKET_PARAMS)
                    if p > 1:
                        env_rev += p
                        env_inv += 1
                    else:
                        env_rev += 1
                        
                self.assertEqual(env_rev, agent_rev, f"Mismatch in {product} for qty {qty}")

    def test_floor_price_units_do_not_increase_inventory(self):
        """Test that units sold at price floor ($1) do not increase market inventory."""
        product = "MELON"
        inv = 10000
        # Find where melon hits floor
        while env_market_price(product, inv, ENV_MARKET_PARAMS) > 1:
            inv += 1
        
        self.assertEqual(env_market_price(product, inv, ENV_MARKET_PARAMS), 1)
        
        self.state.market["inventory"][product] = inv
        
        # Selling 50 melons at floor price should net exactly $50
        qty = 50
        agent_rev = self.econ.expected_sell_value(product, qty)
        self.assertEqual(agent_rev, 50, "Selling at floor price should yield exactly $1 per unit")

if __name__ == '__main__':
    unittest.main()
