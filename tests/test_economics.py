import os
import sys

# Add the project root to sys.path so we can import our agents
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib.util

from kaggle_environments.envs.kaggriculture.kaggriculture import MARKET_PARAMS as TRUE_PARAMS
from kaggle_environments.envs.kaggriculture.kaggriculture import market_price

# Load agent explicitly to avoid conflict with kaggle_environments.agents
spec = importlib.util.spec_from_file_location("v001_baseline", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents", "v001_baseline.py")))
v001 = importlib.util.module_from_spec(spec)
sys.modules["v001_baseline"] = v001
spec.loader.exec_module(v001)

EconomicCalculator = v001.EconomicCalculator

class DummyState:
    def __init__(self):
        self.market = {"inventory": {}, "prices": {}}

def test_all_pricing_curves():
    print("Testing EconomicCalculator pricing curves...")
    dummy_state = DummyState()
    calc = EconomicCalculator(dummy_state)
    
    # Verify MARKET_PARAMS matches
    for product in TRUE_PARAMS:
        print(f"Testing {product}...")
        base = TRUE_PARAMS[product]["base"]
        T = TRUE_PARAMS[product]["T"]
        I0 = 10000
        
        # Test around multiple points: scarcity, equilibrium, glut
        test_points = [
            I0 - 2 * T,
            I0 - T,
            I0 - int(T / 2),
            I0,
            I0 + int(T / 2),
            I0 + T,
            I0 + 2 * T,
            I0 + 10 * T, # extreme glut
        ]
        
        for inv in test_points:
            # Our implementation
            our_price = calc.get_price_at_inventory(product, inv)
            
            # Official environment implementation
            official_price = market_price(product, inv, TRUE_PARAMS)
            
            assert our_price == official_price, f"{product} at inv {inv}: Our Price {our_price} != Official Price {official_price}"
            print(f"  Inv: {inv:<6} -> Price: ${our_price}")
            
    print("\nAll pricing curves match the official environment exactly!")

if __name__ == "__main__":
    test_all_pricing_curves()
