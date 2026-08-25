import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.v018_c_inventory_pacing_v2 import StrategicPlanner, DailyPlanner

class MockEcon:
    def get_price_at_inventory(self, crop, inv):
        return 10.0 # constant for simplicity
    def expected_sell_value(self, crop, qty):
        return 10.0 * qty

class MockState:
    pass

class MockConfig:
    cash_reserve = 500
    crop_policy = 'DYNAMIC'
    min_sell_price = 2
    sell_batch_size = 100

def test_pipeline_pacing_logic():
    state = MockState()
    state.day = 10
    state.hour = 0
    state.money = 2000 # Enough to buy seeds
    state.market = {"inventory": {"WHEAT": 10000, "TOMATO": 10000, "STRAWBERRY": 10000, "MELON": 10000, "CARROT": 10000}}
    state.shed = {}
    state.seeds = {}
    state.my_farm = {"unlocked_quadrants": ["NW"], "tiles": [[None]*10 for _ in range(10)]}
    state.board_size = 10
    state.player = 0
    state.step = 240
    state.private = {}
    state.farmer = (4, 4)
    state.hands = []
    
    # 1. Pipeline <= target -> normal selection
    sp = StrategicPlanner(state, MockEcon(), config=MockConfig())
    sp.metrics = {"crops": {c: {"planted": 0, "deaths": 0} for c in ["WHEAT", "TOMATO", "STRAWBERRY", "MELON", "CARROT"]}, 
                       "workers": {"useful_actions": 1},
                       "farmer": {"useful_actions": 1},
                       "economy": {"worker_spending": 2}}
    planner = DailyPlanner(state, MockEcon(), sp)
    planner.plan_tasks()
    buy_tasks = [t for t in planner.tasks if t.action_type == "BUY_SEED"]
    assert len(buy_tasks) > 0, "Should buy seeds"
    
    # 2. Pipeline > target -> crop rejected
    # Inject high market inventory to simulate pipeline > 20
    state.market["inventory"] = {c: 10030 for c in ["WHEAT", "TOMATO", "STRAWBERRY", "MELON", "CARROT"]}
    state.market["inventory"]["STRAWBERRY"] = 10000
    
    planner = DailyPlanner(state, MockEcon(), sp)
    planner.plan_tasks()
    buy_tasks = [t for t in planner.tasks if t.action_type == "BUY_SEED"]
    assert len(buy_tasks) > 0
    assert buy_tasks[0].kwargs["product"] == "STRAWBERRY", "Should only pick STRAWBERRY since others are rejected"
    
    # 3. Market inventory still determines price
    class TrackingEcon:
        def __init__(self):
            self.calls = []
        def get_price_at_inventory(self, crop, inv):
            self.calls.append((crop, inv))
            return 10.0
        def expected_sell_value(self, crop, qty):
            return 10.0 * qty
            
    econ = TrackingEcon()
    planner = DailyPlanner(state, econ, sp)
    planner.plan_tasks()
    calls_for_strawberry = [inv for (c, inv) in econ.calls if c == "STRAWBERRY"]
    assert calls_for_strawberry[0] == 10000
    assert calls_for_strawberry[1] == 10001
    
    # 4. Pipeline doesn't alter price
    state.shed["MELON"] = 15
    state.market["inventory"]["MELON"] = 10000
    
    econ = TrackingEcon()
    planner = DailyPlanner(state, econ, sp)
    planner.plan_tasks()
    calls_for_melon = [inv for (c, inv) in econ.calls if c == "MELON"]
    if len(calls_for_melon) > 0:
        assert calls_for_melon[0] == 10000
        assert calls_for_melon[1] == 10001
        
    # 6. No infinite rejection loop
    state.market["inventory"] = {c: 10050 for c in ["WHEAT", "TOMATO", "STRAWBERRY", "MELON", "CARROT"]}
    planner = DailyPlanner(state, MockEcon(), sp)
    planner.plan_tasks()
    buy_tasks = [t for t in planner.tasks if t.action_type == "BUY_SEED"]
    assert len(buy_tasks) == 0, "Should buy no seeds if all rejected"
    
    print("All C1 pacing tests passed!")

if __name__ == "__main__":
    test_pipeline_pacing_logic()
