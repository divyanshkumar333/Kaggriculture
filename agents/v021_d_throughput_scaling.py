from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
import math
import os
import json
import collections
import numpy as np
from scipy.optimize import linear_sum_assignment

# ==========================================
# Metrics Tracking
# ==========================================
_METRICS = collections.defaultdict(lambda: {
    "workers": {"hired": 0, "cost": 0, "active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0, "max_active": 0},
    "farmer": {"active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0},
    "economy": {"total_spending": 0, "total_revenue": 0, "seed_spending": 0, "worker_spending": 0},
    "crops": collections.defaultdict(lambda: {"planted": 0, "watered": 0, "harvested": 0, "deaths": 0}),
    "market": collections.defaultdict(lambda: {"sold": 0, "revenue": 0}),
    "water": {"generated": 0, "completed": 0, "misses": 0},
    "labor": {"required_sum": 0, "available_sum": 0, "deficit_sum": 0, "surplus_sum": 0, "cycles": 0},
    "spatial": {
        "fragmentation_sum": 0,
        "isolated_clusters": 0,
        "cluster_count_sum": 0,
        "mean_cluster_size_sum": 0,
        "max_cluster_size_sum": 0,
        "inter_cluster_dist_sum": 0,
        "future_task_density_sum": 0,
        "samples": 0
    },
    "v018": {
        "batches": [],
        "blocked_planting_quantity": 0,
        "empty_tile_days": 0,
        "productive_tile_days": 0,
        "premium_crop_quantity": 0,
        "staple_crop_quantity": 0,
        "premium_revenue": 0,
        "staple_revenue": 0,
        "filler_seed_cost": 0,
        "filler_labor_cost": 0,
        "filler_revenue": 0,
        "planting_prices": [],
        "harvest_prices": [],
        "sale_prices": [],
        "pipelines_at_planting": [],
        "pipelines_at_harvest": []
    },
    "timing": {
        "plants_by_crop": collections.defaultdict(list),
        "revenue_by_crop": collections.defaultdict(int),
        "seeds_purchased_by_crop": collections.defaultdict(int),
        "late_season_seeds_purchased": 0,
        "late_season_crops_planted": 0,
        "revenue_before_20": 0,
        "revenue_after_20": 0,
        "seeds_purchased_after_profitable": 0
    },
    "_prev_plants": {}
})

class MetricsTracker:
    @staticmethod
    def get():
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        return _METRICS[seed]
        
    @staticmethod
    def track_plants(state):
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        m = _METRICS[seed]
        
        current_plants = {}
        for y, row in enumerate(state.my_farm.get("tiles", [])):
            for x, tile in enumerate(row):
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    current_plants[(x, y)] = tile
                    
        for loc, prev_plant in m["_prev_plants"].items():
            if loc not in current_plants:
                tile = state.get_tile(loc[0], loc[1])
                if isinstance(tile, dict) and tile.get("kind") == "WEED":
                    m["crops"][prev_plant["crop"]]["deaths"] += 1
                    
        if state.hour == 0 and state.day > 0:
            for loc, plant in m["_prev_plants"].items():
                if plant.get("consecutive_unwatered", 0) > 0 and not plant.get("watered_today", True):
                    m["water"]["misses"] += 1
                    
        plants = list(current_plants.keys())
        if len(plants) > 1:
            total_dist = 0
            pairs = 0
            for i in range(len(plants)):
                for j in range(i+1, len(plants)):
                    total_dist += abs(plants[i][0] - plants[j][0]) + abs(plants[i][1] - plants[j][1])
                    pairs += 1
            m["spatial"]["fragmentation_sum"] += (total_dist / pairs)
            m["spatial"]["samples"] += 1
                    
        m["_prev_plants"] = current_plants
    
    @staticmethod
    def save(player, step, final_money, shed=None, actions=None, day=None):
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        m = _METRICS[seed]
        m["economy"]["final_money"] = final_money
        if shed:
            m["final_shed"] = shed
            
        total_worker_turns = m["workers"]["active_turns"] + m["workers"]["idle_turns"]
        useful = m["farmer"]["useful_actions"] + m["workers"]["useful_actions"]
        total_movement = m["farmer"]["movement_actions"] + m["workers"]["movement_actions"]
        
        m["efficiency"] = {
            "worker_utilization_pct": m["workers"]["active_turns"] / max(1, total_worker_turns) * 100,
            "farmer_utilization_pct": m["farmer"]["active_turns"] / max(1, m["farmer"]["active_turns"] + m["farmer"]["idle_turns"]) * 100,
            "useful_actions_total": useful,
            "movement_efficiency_pct": useful / max(1, useful + total_movement) * 100,
            "average_workers_day": m["workers"]["hired"] / 30.0,
            "max_workers": m["workers"]["max_active"]
        }

# ==========================================
# 1. Models & Task System
# ==========================================
class Task:
    def __init__(self, action_type, priority, location=None, kwargs=None):
        self.action_type = action_type # WATER, HARVEST, PLANT, BUY_SEED, SELL, HIRE, BUY_LAND
        self.priority = priority
        self.location = location
        self.kwargs = kwargs or {}
        self.assigned_worker = None

    def __repr__(self):
        return f"Task({self.action_type}, prio={self.priority}, loc={self.location}, kwargs={self.kwargs})"

def is_ready_to_harvest(crop_name, planted_day, current_day):
    crop_info = CROPS.get(crop_name)
    if not crop_info:
        return False
    crop_age = current_day - planted_day
    return crop_age >= crop_info["first_yield_day"]

# ==========================================
# 2. Game State Parser
# ==========================================
class GameState:
    def __init__(self, obs):
        self.player = obs.get("player", 0)
        self.step = obs.get("step", 0)
        self.day = obs.get("day", 0)
        self.hour = obs.get("hour", 0)
        self.farms = obs.get("farms", [])
        self.my_farm = self.farms[self.player] if self.farms else {}
        self.market = obs.get("market", {})
        self.town = obs.get("town", {})
        self.private = obs.get("private", {})
        
        self.board_size = len(self.my_farm.get("tiles", []))
        self.money = self.my_farm.get("money", 0)
        self.farmer = self.my_farm.get("farmer", [0, 0])
        self.hands = self.my_farm.get("hands", [])
        self.hires_today = self.my_farm.get("hires_today", 0)
        self.unlocked_quads = self.my_farm.get("unlocked_quadrants", [])
        
        self.shed = self.private.get("shed", {})
        self.seeds = self.private.get("seeds", {})
        
    def get_tile(self, x, y):
        return self.my_farm.get("tiles", [])[y][x]

# ==========================================
# 3. Economic Calculator
# ==========================================
MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60}
}

class EconomicCalculator:
    def __init__(self, state: GameState):
        self.state = state

    def _eval_func(self, func_name, x, T):
        x = max(0.0, x)
        if func_name == "linear": return x
        elif func_name == "sq": return x * x
        elif func_name == "sqrt": return math.sqrt(x)
        elif func_name == "log": return math.log(1.0 + x)
        elif func_name == "log10": return math.log10(1.0 + x)
        elif func_name == "hinge":
            if not T or T <= 0: return x
            u = x / T
            return u + 8.0 * max(0.0, u - 1.0)**2
        return x

    def get_price_at_inventory(self, product, inv):
        params = MARKET_PARAMS.get(product)
        if not params: return 1
        base = params["base"]
        I0 = params["I0"]
        T = params["T"]
        diff = abs(inv - I0)
        
        if inv < I0:
            sign = 1
            f_name = params["below_func"]
            target = params["below_target"]
        elif inv > I0:
            sign = -1
            f_name = params["above_func"]
            target = params["above_target"]
        else:
            return base
            
        amp = (target * base) / self._eval_func(f_name, T, T)
        val = self._eval_func(f_name, diff, T)
        price = base + sign * amp * val
        return max(1, int(round(price)))

    def expected_sell_value(self, product, quantity):
        current_inv = self.state.market.get("inventory", {}).get(product, 10000)
        total_rev = 0
        inv = current_inv
        for _ in range(quantity):
            price = self.get_price_at_inventory(product, inv)
            if price <= 1:
                total_rev += 1
            else:
                total_rev += price
                inv += 1
        return total_rev

    def get_hire_cost(self, n):
        def fib(x):
            if x <= 1: return 1
            return fib(x-1) + fib(x-2)
        return fib(n)

# ==========================================
# 4. Strategic Planner (Dynamic Gating)
# ==========================================
class StrategyConfig:
    def __init__(self,
                 crop_policy="MELON",
                 min_sell_price=1,
                 sell_batch_size=10,
                 worker_roi_threshold=15.0,
                 cash_reserve=50):
        self.crop_policy = crop_policy
        self.min_sell_price = min_sell_price
        self.sell_batch_size = sell_batch_size
        self.worker_roi_threshold = worker_roi_threshold
        self.cash_reserve = cash_reserve

class StrategicPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator, config: StrategyConfig = None):
        self.state = state
        self.econ = econ
        self.config = config or StrategyConfig()

    def get_daily_plant_cap(self, empty_tiles_count):
        # Stage 1 (Days 0-10): Strict 4-seed batch cap to protect bootstrap working capital
        if self.state.day < 11 or self.state.money < 4000:
            return 4
        
        # Stage 2 (Day 11+ Post-Melon Liquidity): Scale planting throughput to fill land rapidly
        if self.state.money >= 12000 and empty_tiles_count >= 10:
            return 10
        elif self.state.money >= 4000 and empty_tiles_count >= 6:
            return 8
        return 6

# ==========================================
# 5. Daily Planner (Gated Expansion)
# ==========================================
class DailyPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator, strategy: StrategicPlanner):
        self.state = state
        self.econ = econ
        self.strategy = strategy
        self.tasks = []

    def plan_tasks(self):
        farm_tiles = self.state.my_farm.get("tiles", [])
        simulated_seeds = dict(self.state.seeds)
        remaining_days = 30 - self.state.day
        
        existing_crops = []
        empty_tiles = []
        
        # 1. Scan Tiles & Generate Water/Harvest Tasks
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    crop_name = tile.get("crop", "")
                    existing_crops.append((x, y, crop_name))
                    
                    # WATER Task
                    if not tile.get("watered_today", True):
                        consecutive = tile.get("consecutive_unwatered", 0)
                        turns_until = (24 - self.state.hour) if consecutive >= 1 else (48 - self.state.hour)
                        crop_info = CROPS.get(crop_name, {})
                        expected_rev = self.econ.expected_sell_value(crop_name, crop_info.get("max_yield", 4))
                        urgency = expected_rev / max(1, turns_until)
                        self.tasks.append(Task("WATER", 1000, (x, y), {"urgency_score": urgency, "value_score": 0}))
                        
                    # HARVEST Task
                    if tile.get("yield_units", 0) > 0 and is_ready_to_harvest(crop_name, tile.get("planted_day", 0), self.state.day):
                        crop_info = CROPS.get(crop_name, {})
                        value = self.econ.expected_sell_value(crop_name, tile.get("yield_units", 0))
                        self.tasks.append(Task("HARVEST", 1500, (x, y), {"urgency_score": 50, "value_score": value}))
                elif tile is None:
                    empty_tiles.append((x, y))

        # Dynamic Plant Cap
        DAILY_PLANT_CAP = self.strategy.get_daily_plant_cap(len(empty_tiles))

        # 2. Market Sales
        for product, qty in self.state.shed.items():
            if qty > 0:
                self.tasks.append(Task("SELL", 5, kwargs={"product": product, "quantity": min(10, qty)}))

        # 3. Dynamic Crop Selection
        target_crop = self.strategy.config.crop_policy
        best_crop = self.strategy.config.crop_policy
        best_profit_per_action = -999999
        crop_actions = {"WHEAT": 5, "CARROT": 4, "TOMATO": 15, "STRAWBERRY": 20, "MELON": 12}
        crop_max_yield = {"WHEAT": 6, "CARROT": 4, "TOMATO": 16, "STRAWBERRY": 16, "MELON": 6}
        
        for crop_name in crop_actions.keys():
            seed_cost = CROPS.get(crop_name, {}).get("seed", 999)
            crop_info = CROPS.get(crop_name, {})
            first_yield = crop_info.get("first_yield_day", 999)
            if remaining_days - 1 >= first_yield:
                current_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
                expected_rev = sum(self.econ.get_price_at_inventory(crop_name, current_inv + i) for i in range(crop_max_yield[crop_name]))
                profit_per_action = (expected_rev - seed_cost) / crop_actions[crop_name]
                if profit_per_action > best_profit_per_action:
                    best_profit_per_action = profit_per_action
                    best_crop = crop_name
        target_crop = best_crop

        # 4. Dynamic Operating Reserve
        operating_reserve = self.strategy.config.cash_reserve + (DAILY_PLANT_CAP * CROPS.get(target_crop, {}).get("seed", 80))

        # 5. Fractional Seed Replenishment
        current_seeds = self.state.seeds.get(target_crop, 0)
        if self.state.hour == 0 or current_seeds == 0:
            needed_seeds = min(DAILY_PLANT_CAP - current_seeds, len(empty_tiles))
            if needed_seeds > 0 and self.state.money > operating_reserve + (CROPS[target_crop]["seed"] * needed_seeds):
                if remaining_days - 1 >= CROPS.get(target_crop, {}).get("first_yield_day", 999):
                    buy_qty = min(self.state.money // CROPS[target_crop]["seed"], needed_seeds)
                    if buy_qty > 0:
                        self.tasks.append(Task("BUY_SEED", 50, kwargs={"product": target_crop, "quantity": buy_qty}))

        # 6. Planting Tasks
        for crop in list(simulated_seeds.keys()):
            if simulated_seeds[crop] > DAILY_PLANT_CAP:
                simulated_seeds[crop] = DAILY_PLANT_CAP
                
        total_seeds_to_plant = sum(simulated_seeds.values())
        fx, fy = self.state.farmer
        
        while total_seeds_to_plant > 0 and empty_tiles:
            seed_to_plant = None
            for available_crop, amount in list(simulated_seeds.items()):
                if amount > 0:
                    first_yield = CROPS.get(available_crop, {}).get("first_yield_day", 999)
                    if remaining_days - 1 >= first_yield:
                        seed_to_plant = available_crop
                        break
                    else:
                        simulated_seeds[available_crop] = 0
            if not seed_to_plant:
                break
                
            best_tile = min(empty_tiles, key=lambda t: abs(fx - t[0]) + abs(fy - t[1]))
            crop_info = CROPS.get(seed_to_plant, {})
            self.tasks.append(Task("PLANT", 30, best_tile, {"crop": seed_to_plant, "urgency_score": 0, "value_score": 50}))
            simulated_seeds[seed_to_plant] -= 1
            total_seeds_to_plant -= 1
            empty_tiles.remove(best_tile)

        # 7. Economically Gated Land Expansion
        # Only buy land when current land is almost full (empty_tiles <= 5) and we have adequate time to profit
        if len(empty_tiles) <= 5 and remaining_days >= 10:
            n_unlocked = len(self.state.unlocked_quads)
            land_prices = [1000, 2000, 4000]
            if 1 <= n_unlocked <= 3:
                next_cost = land_prices[n_unlocked - 1]
                # In Stage 2, require remaining cash > operating_reserve after purchase
                if self.state.money > next_cost + operating_reserve:
                    self.tasks.append(Task("BUY_LAND", priority=100))

        self.tasks.sort(key=lambda t: t.priority)
        return self.tasks

# ==========================================
# 6. Task Allocator (Workload-Matched Labor)
# ==========================================
class TaskAllocator:
    def __init__(self, state: GameState, econ: EconomicCalculator, tasks, strategy):
        self.state = state
        self.econ = econ
        self.tasks = tasks
        self.strategy = strategy
    
    def allocate(self):
        active_workers = 1 + len(self.state.hands)
        farm_tiles = self.state.my_farm.get("tiles", [])
        
        metrics = MetricsTracker.get()
        metrics["workers"]["max_active"] = max(metrics["workers"]["max_active"], active_workers)
        
        # Count total active crops on farm
        total_crops = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("kind") == "PLANT")
        
        # Determine target workers to guarantee 100% watering coverage without idle waste
        # 1 farmer (24 actions) covers up to 24 crops.
        # 1 hand (48 total actions) covers up to 45 crops.
        # 2 hands (72 total actions) covers up to 65 crops.
        # 3 hands (96 total actions) covers up to 85 crops.
        if total_crops <= 25:
            target_hands = 1
        elif total_crops <= 48:
            target_hands = 1 if self.state.day < 11 else 2
        elif total_crops <= 68:
            target_hands = 2 if self.state.day < 11 else 3
        else:
            target_hands = 3 if self.state.day < 11 else 4
            
        current_hands = len(self.state.hands)
        hires_today = self.state.hires_today
        cost_of_next_hire = self.econ.get_hire_cost(hires_today)
        operating_reserve = self.strategy.config.cash_reserve + 200
        
        # Hire at Hour 0-2 if below target workforce and cash is protected
        if current_hands < target_hands and self.state.hour <= 2:
            if self.state.money > cost_of_next_hire + operating_reserve:
                self.tasks.append(Task("HIRE", 1))

        return {}

# ==========================================
# 7. Action Executor (Market Priority Order)
# ==========================================
class ActionExecutor:
    def __init__(self, state: GameState, econ: EconomicCalculator):
        self.state = state
        self.econ = econ
        self.metrics = MetricsTracker.get()
        
    def step_toward(self, fx, fy, tx, ty):
        if fx > tx: return "WEST"
        if fx < tx: return "EAST"
        if fy > ty: return "NORTH"
        if fy < ty: return "SOUTH"
        return "PASS"
    
    def _order_priority(self, action):
        op = action[0]
        if op == "HIRE": return 100000
        elif op == "BUY_LAND": return 90000
        elif op == "BUY_SEED": return 80000
        elif op == "SELL":
            product = action[1]
            qty = action[2] if len(action) > 2 else 1
            current_price = self.state.market.get("prices", {}).get(product, 1)
            return 1000 + (current_price * qty)
        return 0
    
    def execute(self, tasks, assignments):
        market_actions = []
        field_tasks = []
        
        for t in tasks:
            if t.action_type in ["SELL", "BUY_SEED", "HIRE", "BUY_LAND"]:
                if t.action_type == "SELL":
                    market_actions.append(["SELL", t.kwargs["product"], t.kwargs["quantity"]])
                elif t.action_type == "BUY_SEED":
                    market_actions.append(["BUY_SEED", t.kwargs["product"], t.kwargs["quantity"]])
                elif t.action_type == "HIRE":
                    market_actions.append(["HIRE"])
                elif t.action_type == "BUY_LAND":
                    market_actions.append(["BUY_LAND"])
            elif t.location is not None:
                field_tasks.append(t)
                
        units = [self.state.farmer] + self.state.hands
        unit_actions = []
        assigned_targets = [None] * len(units)

        if field_tasks and units:
            n_workers = len(units)
            m_tasks = len(field_tasks)
            cost_matrix = np.zeros((n_workers, m_tasks))
            
            for i, (ux, uy) in enumerate(units):
                for j, target in enumerate(field_tasks):
                    tx, ty = target.location
                    dist = abs(ux - tx) + abs(uy - ty)
                    if target.priority >= 2000:
                        cost = -1000000 + dist * 10
                    else:
                        u_score = target.kwargs.get("urgency_score", 0)
                        cost = (dist * 10) - target.priority - u_score
                    cost_matrix[i, j] = cost
            
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            for i, j in zip(row_ind, col_ind):
                assigned_targets[i] = field_tasks[j]

        for ui, (ux, uy) in enumerate(units):
            action = ["PASS"]
            target = assigned_targets[ui]
            
            if target is not None:
                tx, ty = target.location
                if ux == tx and uy == ty:
                    if target.action_type == "PLANT":
                        action = ["PLANT", target.kwargs["crop"]]
                    elif target.action_type in ["WATER", "HARVEST"]:
                        action = [target.action_type]
                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
                    
            unit_actions.append(action)
            
        farmer_action = unit_actions[0] if unit_actions else ["PASS"]
        hands_actions = unit_actions[1:] if len(unit_actions) > 1 else []
        
        market_actions.sort(key=lambda a: self._order_priority(a), reverse=True)
        market_actions = market_actions[:10]
        
        return {
            "farmer": farmer_action,
            "hands": hands_actions,
            "market": market_actions
        }

# ==========================================
# Main Agent Entrypoint
# ==========================================
def agent(obs):
    try:
        state = GameState(obs)
        MetricsTracker.track_plants(state)
        
        if not state.my_farm:
            return {"farmer": ["PASS"], "hands": [], "market": []}
            
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        allocator = TaskAllocator(state, econ, tasks, strategy)
        assignments = allocator.allocate()
        
        executor = ActionExecutor(state, econ)
        actions = executor.execute(tasks, assignments)
        
        MetricsTracker.save(state.player, state.step, state.money, state.private.get("shed", {}), actions=actions, day=state.day)
        return actions
        
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
