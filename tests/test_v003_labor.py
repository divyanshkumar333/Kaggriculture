import unittest
from agents.v003_dynamic_labor import TaskAllocator, Task, GameState, EconomicCalculator, StrategicPlanner

class MockGameState:
    def __init__(self, hour, hands, field_tasks_count, uninstantiated_plant_tasks, money, hires_today):
        self.hour = hour
        self.hands = hands
        self.money = money
        self.hires_today = hires_today
        self.board_size = 10
        self.farmer = (0, 0)
        
        # Mock tiles
        self.my_farm = {"tiles": [[None]*10 for _ in range(10)]}
        
        # Adjust empty_unlocked so that uninstantiated_plant_tasks matches requested
        # empty_unlocked = uninstantiated_plant_tasks + queued_plant_tasks
        # We'll just leave it empty and pass the mocked list
        
        self.tasks = []
        for i in range(field_tasks_count):
            self.tasks.append(Task("WATER", 10, (i%10, i//10)))
            
        # Add uninstantiated tasks by forcing tiles to be None
        # the agent counts empty tiles
        # if we want 0 uninstantiated, we just make them not None
        if uninstantiated_plant_tasks == 0:
            for y in range(10):
                for x in range(10):
                    self.my_farm["tiles"][y][x] = {"kind": "LOCKED"}

class MockEcon:
    def get_hire_cost(self, n):
        def fib(x):
            if x <= 1: return 1
            return fib(x-1) + fib(x-2)
        return fib(n)

class MockConfig:
    def __init__(self):
        self.worker_roi_threshold = 15.0
        self.cash_reserve = 50

class MockStrategy:
    def __init__(self):
        self.config = MockConfig()

class TestV003Labor(unittest.TestCase):
    def setUp(self):
        # We can bypass MetricsTracker in tests by mocking it, or just let it use its global
        import os
        os.environ["KAGGRICULTURE_SEED"] = "test"

    def _run_allocator(self, hour, hands_count, tasks_count, uninstantiated, money, hires_today=0, roi=15.0):
        hands = [(0, 0) for _ in range(hands_count)]
        state = MockGameState(hour, hands, tasks_count, uninstantiated, money, hires_today)
        econ = MockEcon()
        strategy = MockStrategy()
        strategy.config.worker_roi_threshold = roi
        
        allocator = TaskAllocator(state, econ, state.tasks, strategy)
        allocator.allocate()
        
        hires = [t for t in allocator.tasks if t.action_type == "HIRE"]
        return len(hires)

    def test_A_no_deficit(self):
        # 1 farmer, 24 remaining actions. 10 tasks.
        # required: min_dist + 10 * 2 = 0 + 20 = 20.
        # Deficit = 20 - 24 = -4. No hire.
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=10, uninstantiated=0, money=100)
        self.assertEqual(hires, 0)

    def test_B_genuine_deficit(self):
        # 1 farmer, 24 actions. 30 tasks = 60 actions.
        # Deficit = 60 - 24 = 36. Should hire.
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=30, uninstantiated=0, money=100)
        self.assertEqual(hires, 1)

    def test_C_late_day(self):
        # 1 farmer, 3 remaining actions (hour 21). 30 tasks = 60 actions.
        # Should not hire because remaining_turns <= 3
        hires = self._run_allocator(hour=21, hands_count=0, tasks_count=30, uninstantiated=0, money=100)
        self.assertEqual(hires, 0)

    def test_D_insufficient_cash(self):
        # Big deficit, but only 50 cash (equal to reserve). 1 hire costs 1.
        # Need money > cost + reserve. 50 > 1 + 50 is False.
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=30, uninstantiated=0, money=50)
        self.assertEqual(hires, 0)

    def test_E_marginal_roi(self):
        # ROI threshold is 15. Next hire costs 21 (hires_today=7 -> fib(7)=21)
        # 15 > 21 is False. Should not hire.
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=30, uninstantiated=0, money=100, hires_today=7, roi=15.0)
        self.assertEqual(hires, 0)

    def test_F_no_infinite_hiring(self):
        # Even with massive deficit, should only queue 1 HIRE task per cycle
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=100, uninstantiated=0, money=1000)
        self.assertEqual(hires, 1)
        
    def test_G_regression(self):
        # Baseline regression: check that if uninstantiated tasks exist, they trigger hiring
        # 1 farmer, 24 actions. 0 existing tasks, but 50 uninstantiated tasks -> 100 required actions.
        hires = self._run_allocator(hour=0, hands_count=0, tasks_count=0, uninstantiated=50, money=1000)
        self.assertEqual(hires, 1)

if __name__ == '__main__':
    unittest.main()
