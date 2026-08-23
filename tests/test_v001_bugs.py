import unittest
from agents.v001_baseline import is_ready_to_harvest, GameState, EconomicCalculator, StrategicPlanner, DailyPlanner, TaskAllocator, ActionExecutor, Task

class TestV001Bugs(unittest.TestCase):
    def setUp(self):
        # A basic generic observation for testing
        self.base_obs = {
            "player": 0,
            "step": 0,
            "day": 0,
            "hour": 0,
            "farms": [
                {
                    "money": 3000,
                    "farmer": [0, 0],
                    "hands": [],
                    "hires_today": 0,
                    "tiles": [[None for _ in range(10)] for _ in range(10)]
                },
                {
                    "money": 3000,
                    "farmer": [0, 0],
                    "hands": [],
                    "hires_today": 0,
                    "tiles": [[None for _ in range(10)] for _ in range(10)]
                }
            ],
            "private": {
                "shed": {},
                "seeds": {},
                "inventories": [{}]
            },
            "market": {
                "inventory": {"MELON": 10000},
                "prices": {"MELON": 250}
            }
        }

    # ---------------------------------------------------------
    # Test A: Immature crop (verify HARVEST is NOT selected)
    # ---------------------------------------------------------
    def test_immature_crop_no_harvest(self):
        obs = dict(self.base_obs)
        obs["day"] = 5
        # Planted day 0, day 5 means age 5. Melon first_yield_day is 12.
        obs["farms"][0]["tiles"][0][0] = {
            "kind": "PLANT",
            "crop": "MELON",
            "planted_day": 0,
            "watered_today": True,
            "yield_units": 1
        }
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        harvest_tasks = [t for t in tasks if t.action_type == "HARVEST"]
        
        self.assertEqual(len(harvest_tasks), 0, "Immature crop should NOT trigger a HARVEST task.")
        self.assertFalse(is_ready_to_harvest("MELON", 0, 5))

    # ---------------------------------------------------------
    # Test B: Mature crop (verify HARVEST is selected)
    # ---------------------------------------------------------
    def test_mature_crop_harvest(self):
        obs = dict(self.base_obs)
        obs["day"] = 12
        # Planted day 0, day 12 means age 12. Melon first_yield_day is 12.
        obs["farms"][0]["tiles"][0][0] = {
            "kind": "PLANT",
            "crop": "MELON",
            "planted_day": 0,
            "watered_today": True,
            "yield_units": 1
        }
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        harvest_tasks = [t for t in tasks if t.action_type == "HARVEST"]
        
        self.assertEqual(len(harvest_tasks), 1, "Mature crop SHOULD trigger a HARVEST task.")
        self.assertTrue(is_ready_to_harvest("MELON", 0, 12))

    # ---------------------------------------------------------
    # Test C: Harvest -> Sell & Test D: Dependency Integrity
    # ---------------------------------------------------------
    def test_dependency_integrity_and_sell(self):
        obs = dict(self.base_obs)
        obs["private"]["shed"] = {"MELON": 15}
        obs["market"]["inventory"]["MELON"] = 0  # To ensure high prices
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        
        # Test D: verify econ is present
        planner = DailyPlanner(state, econ, strategy)
        self.assertTrue(hasattr(planner, "econ"))
        self.assertIsNotNone(planner.econ)
        
        # Execute selling decision
        tasks = planner.plan_tasks()
        sell_tasks = [t for t in tasks if t.action_type == "SELL"]
        
        # We have 15 melons. The agent should queue them up to 10 at a time.
        self.assertEqual(len(sell_tasks), 1, "Should queue one SELL task.")
        self.assertEqual(sell_tasks[0].kwargs["quantity"], 10, "Should queue exactly 10 items to sell.")
        
        # Pass to executor
        allocator = TaskAllocator(state, econ, tasks)
        assignments = allocator.allocate()
        
        executor = ActionExecutor(state, econ)
        result = executor.execute(tasks, assignments)
        market_actions = result["market"]
        
        # Verify market actions actually produced a list we return to the environment
        self.assertTrue(any(a[0] == "SELL" and a[1] == "MELON" and a[2] == 10 for a in market_actions))

    # ---------------------------------------------------------
    # Test E: Worker regression
    # ---------------------------------------------------------
    def test_worker_regression(self):
        obs = dict(self.base_obs)
        # Add a farm hand
        obs["farms"][0]["hands"] = [[1, 1]]
        # Give two tasks to do (water two tiles) so both farmer and worker get one
        obs["farms"][0]["tiles"][2][2] = {
            "kind": "PLANT",
            "crop": "MELON",
            "planted_day": 0,
            "watered_today": False,
            "yield_units": 1
        }
        obs["farms"][0]["tiles"][3][3] = {
            "kind": "PLANT",
            "crop": "MELON",
            "planted_day": 0,
            "watered_today": False,
            "yield_units": 1
        }
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        
        allocator = TaskAllocator(state, econ, tasks)
        assignments = allocator.allocate()
        
        executor = ActionExecutor(state, econ)
        result = executor.execute(tasks, assignments)
        hands_actions = result["hands"]
        
        self.assertTrue(len(hands_actions) > 0, "Worker should have an action returned.")
        self.assertNotEqual(hands_actions[0], ["PASS"], "Worker should not permanently PASS.")
        # Worker is at [1,1] and needs to water [2,2], so it should step toward it (EAST or SOUTH)
        self.assertIn(hands_actions[0][0], ["EAST", "SOUTH"])


    # ---------------------------------------------------------
    # Test 1: One Seed / Many Tiles
    # ---------------------------------------------------------
    def test_one_seed_many_tiles(self):
        obs = dict(self.base_obs)
        obs["private"]["seeds"] = {"MELON": 1}
        # By default base_obs has 100 None tiles (10x10)
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        plant_tasks = [t for t in tasks if t.action_type == "PLANT"]
        self.assertEqual(len(plant_tasks), 1, "Should generate exactly 1 PLANT task for 1 seed.")

    # ---------------------------------------------------------
    # Test 2: Five Seeds / Many Tiles
    # ---------------------------------------------------------
    def test_five_seeds_many_tiles(self):
        obs = dict(self.base_obs)
        obs["private"]["seeds"] = {"MELON": 5}
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        plant_tasks = [t for t in tasks if t.action_type == "PLANT"]
        self.assertEqual(len(plant_tasks), 5, "Should generate exactly 5 PLANT tasks for 5 seeds.")

    # ---------------------------------------------------------
    # Test 3: Zero Seeds
    # ---------------------------------------------------------
    def test_zero_seeds_many_tiles(self):
        obs = dict(self.base_obs)
        obs["private"]["seeds"] = {"MELON": 0}
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        plant_tasks = [t for t in tasks if t.action_type == "PLANT"]
        self.assertEqual(len(plant_tasks), 0, "Should generate exactly 0 PLANT tasks for 0 seeds.")

    # ---------------------------------------------------------
    # Test 4: More Seeds Than Tiles
    # ---------------------------------------------------------
    def test_more_seeds_than_tiles(self):
        obs = dict(self.base_obs)
        obs["private"]["seeds"] = {"MELON": 10}
        # Restrict board to only 3 eligible tiles
        for y in range(10):
            for x in range(10):
                obs["farms"][0]["tiles"][y][x] = {"kind": "LOCKED"} # fill with locked
        
        obs["farms"][0]["tiles"][0][0] = None
        obs["farms"][0]["tiles"][0][1] = None
        obs["farms"][0]["tiles"][0][2] = None
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        plant_tasks = [t for t in tasks if t.action_type == "PLANT"]
        self.assertEqual(len(plant_tasks), 3, "Should generate exactly 3 PLANT tasks because only 3 tiles are eligible.")

    # ---------------------------------------------------------
    # Test 5: Worker Allocation
    # ---------------------------------------------------------
    def test_worker_allocation_phantom_tasks(self):
        obs = dict(self.base_obs)
        obs["private"]["seeds"] = {"MELON": 1}
        # 100 empty tiles available
        # 5 hands
        obs["farms"][0]["hands"] = [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
        
        state = GameState(obs)
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        allocator = TaskAllocator(state, econ, tasks)
        assignments = allocator.allocate()
        executor = ActionExecutor(state, econ)
        result = executor.execute(tasks, assignments)
        
        # 1 seed = 1 PLANT task. So only 1 unit should receive a PLANT action.
        all_unit_actions = [result["farmer"]] + result["hands"]
        plant_actions = [a for a in all_unit_actions if a[0] == "PLANT"]
        
        self.assertEqual(len(plant_actions), 1, "Only 1 unit should execute a PLANT action when there is 1 seed.")


if __name__ == "__main__":
    unittest.main()
