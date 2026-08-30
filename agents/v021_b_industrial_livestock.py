from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS, ANIMALS
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
    "economy": {"total_spending": 0, "total_revenue": 0, "seed_spending": 0, "worker_spending": 0, "animal_spending": 0},
    "crops": collections.defaultdict(lambda: {"planted": 0, "watered": 0, "harvested": 0, "deaths": 0}),
    "animals": collections.defaultdict(lambda: {"bought": 0, "fed": 0, "cared": 0, "harvested": 0, "fertilizer": 0}),
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
        self.action_type = action_type # WATER, HARVEST, PLANT, FEED, CARE, COLLECT_FERTILIZER, BUILD_PASTURE, BUILD_COOP, PLACE, BUY_SEED, BUY_ANIMAL, BUY_PRODUCT, SELL, HIRE, BUY_LAND
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
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40}
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
# 4. Strategic Planner
# ==========================================
class StrategyConfig:
    def __init__(self,
                 crop_policy="MELON",
                 min_sell_price=1,
                 sell_batch_size=10,
                 worker_roi_threshold=15.0,
                 cash_reserve=50,
                 max_cows=8,
                 max_sheep=4,
                 max_geese=4):
        self.crop_policy = crop_policy
        self.min_sell_price = min_sell_price
        self.sell_batch_size = sell_batch_size
        self.worker_roi_threshold = worker_roi_threshold
        self.cash_reserve = cash_reserve
        self.max_cows = max_cows
        self.max_sheep = max_sheep
        self.max_geese = max_geese

class StrategicPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator, config: StrategyConfig = None):
        self.state = state
        self.econ = econ
        self.config = config or StrategyConfig()

# ==========================================
# 5. Daily Planner (Hybrid Crop + Livestock)
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
        simulated_shed = dict(self.state.shed)
        remaining_days = 30 - self.state.day
        
        existing_crops = []
        empty_tiles = []
        pastures = []
        coops = []
        cows_count = 0
        sheep_count = 0
        geese_count = 0
        empty_pastures = []
        empty_coops = []
        wheat_plant_count = 0
        
        # 1. Scan Farm Tiles & Generate Maintenance Tasks
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict):
                    kind = tile.get("kind")
                    if kind == "PLANT":
                        crop_name = tile.get("crop", "")
                        existing_crops.append((x, y, crop_name))
                        if crop_name == "WHEAT":
                            wheat_plant_count += 1
                            
                        # WATER Task
                        if not tile.get("watered_today", True):
                            consecutive = tile.get("consecutive_unwatered", 0)
                            turns_until = (24 - self.state.hour) if consecutive >= 1 else (48 - self.state.hour)
                            crop_info = CROPS.get(crop_name, {})
                            expected_rev = self.econ.expected_sell_value(crop_name, crop_info.get("max_yield", 4))
                            urgency = expected_rev / max(1, turns_until)
                            self.tasks.append(Task("WATER", 1000, (x, y), {"urgency_score": urgency, "value_score": 0}))
                            
                        # HARVEST Crop Task
                        if tile.get("yield_units", 0) > 0 and is_ready_to_harvest(crop_name, tile.get("planted_day", 0), self.state.day):
                            crop_info = CROPS.get(crop_name, {})
                            value = self.econ.expected_sell_value(crop_name, tile.get("yield_units", 0))
                            self.tasks.append(Task("HARVEST", 1500, (x, y), {"urgency_score": 50, "value_score": value}))
                            
                    elif kind == "PASTURE":
                        pastures.append((x, y))
                        animal = tile.get("animal")
                        if not animal:
                            empty_pastures.append((x, y))
                            # If animal in shed, generate PLACE task
                            if simulated_shed.get("COW", 0) > 0:
                                self.tasks.append(Task("PLACE", 2000, (x, y), {"item": "COW"}))
                                simulated_shed["COW"] -= 1
                            elif simulated_shed.get("SHEEP", 0) > 0:
                                self.tasks.append(Task("PLACE", 2000, (x, y), {"item": "SHEEP"}))
                                simulated_shed["SHEEP"] -= 1
                        else:
                            if animal == "COW": cows_count += 1
                            elif animal == "SHEEP": sheep_count += 1
                            
                            # FEED Animal Task (Ultra High Priority - Prevent Escape)
                            if not tile.get("fed_today", True) and simulated_shed.get("WHEAT", 0) > 0:
                                self.tasks.append(Task("FEED", 2500, (x, y), {"urgency_score": 100}))
                                simulated_shed["WHEAT"] -= 1
                            # HARVEST Milk / Wool Task
                            if tile.get("yield_units", 0) > 0:
                                self.tasks.append(Task("HARVEST", 1600, (x, y), {"urgency_score": 80}))
                            # CARE Task (Bank +1 Multiplier)
                            if not tile.get("cared_today", True):
                                self.tasks.append(Task("CARE", 1200, (x, y), {"urgency_score": 30}))
                            # COLLECT_FERTILIZER Task
                            if tile.get("fertilizer_available", False):
                                self.tasks.append(Task("COLLECT_FERTILIZER", 1100, (x, y), {"urgency_score": 20}))
                                
                    elif kind == "COOP":
                        coops.append((x, y))
                        animal = tile.get("animal")
                        if not animal:
                            empty_coops.append((x, y))
                            if simulated_shed.get("GOOSE", 0) > 0:
                                self.tasks.append(Task("PLACE", 2000, (x, y), {"item": "GOOSE"}))
                                simulated_shed["GOOSE"] -= 1
                        else:
                            if animal == "GOOSE": geese_count += 1
                            if not tile.get("fed_today", True) and simulated_shed.get("WHEAT", 0) > 0:
                                self.tasks.append(Task("FEED", 2500, (x, y), {"urgency_score": 100}))
                                simulated_shed["WHEAT"] -= 1
                            if tile.get("yield_units", 0) > 0:
                                self.tasks.append(Task("HARVEST", 1600, (x, y), {"urgency_score": 80}))
                            if not tile.get("cared_today", True):
                                self.tasks.append(Task("CARE", 1200, (x, y), {"urgency_score": 30}))
                            if tile.get("fertilizer_available", False):
                                self.tasks.append(Task("COLLECT_FERTILIZER", 1100, (x, y), {"urgency_score": 20}))
                elif tile is None:
                    empty_tiles.append((x, y))

        total_animals = cows_count + sheep_count + geese_count
        DAILY_PLANT_CAP = 4  # Preserved V020-C batch cap
        
        # 2. Feed Security Guard: If Wheat in shed < 2 days of feed demand, buy Wheat product directly
        wheat_in_shed = self.state.shed.get("WHEAT", 0)
        if total_animals > 0 and wheat_in_shed < (total_animals * 2) and self.state.hour == 0:
            needed_wheat_buy = min(10, (total_animals * 3) - wheat_in_shed)
            if needed_wheat_buy > 0 and self.state.money > needed_wheat_buy * 30 + 100:
                self.tasks.append(Task("BUY_PRODUCT", priority=95, kwargs={"product": "WHEAT", "quantity": needed_wheat_buy}))

        # 3. Market Sales: Queue selling produce while keeping safe feed reserves
        for product, qty in self.state.shed.items():
            if qty > 0:
                if product == "WHEAT":
                    # Retain wheat needed for feeding animals
                    reserved_wheat = total_animals * 2
                    sellable_wheat = max(0, qty - reserved_wheat)
                    if sellable_wheat > 0:
                        self.tasks.append(Task("SELL", 5, kwargs={"product": "WHEAT", "quantity": min(10, sellable_wheat)}))
                else:
                    self.tasks.append(Task("SELL", 5, kwargs={"product": product, "quantity": min(10, qty)}))

        # 4. Livestock Infrastructure & Animal Purchases (Staged Economic Rollout)
        # Operating reserve protecting seed capital ($720)
        operating_reserve = self.strategy.config.cash_reserve + (DAILY_PLANT_CAP * 80)
        
        # Pasture & Cow Purchases (Payback period ~8.5 days; require remaining_days >= 10)
        if remaining_days >= 10:
            # Check if we should purchase animals for existing empty structures
            if empty_pastures and cows_count < self.strategy.config.max_cows:
                if self.state.money > 1500 + operating_reserve and self.state.hour == 0:
                    self.tasks.append(Task("BUY_ANIMAL", priority=90, kwargs={"product": "COW", "quantity": 1}))
            elif empty_pastures and sheep_count < self.strategy.config.max_sheep:
                if self.state.money > 1000 + operating_reserve and self.state.hour == 0:
                    self.tasks.append(Task("BUY_ANIMAL", priority=90, kwargs={"product": "SHEEP", "quantity": 1}))
            elif empty_coops and geese_count < self.strategy.config.max_geese:
                if self.state.money > 300 + operating_reserve and self.state.hour == 0:
                    self.tasks.append(Task("BUY_ANIMAL", priority=90, kwargs={"product": "GOOSE", "quantity": 1}))
                    
            # Check if we should build new Pasture or Coop structures
            target_pastures = min(self.strategy.config.max_cows + self.strategy.config.max_sheep, 8 if self.state.day >= 6 else (4 if self.state.day >= 3 else 2))
            if len(pastures) < target_pastures and not empty_pastures and empty_tiles:
                if self.state.money > 500 + 1500 + operating_reserve:
                    tile_for_pasture = empty_tiles.pop(0)
                    self.tasks.append(Task("BUILD_PASTURE", priority=85, location=tile_for_pasture))

        # 5. Internal Wheat Pipeline & Crop Selection
        # Maintain enough wheat tiles to sustain the herd (1 wheat tile supports 1 animal)
        target_wheat_tiles = max(4, total_animals + 2)
        target_crop = "WHEAT" if wheat_plant_count < target_wheat_tiles else self.strategy.config.crop_policy
        
        # V020-C Crop Evaluator for Non-Wheat crops
        if target_crop != "WHEAT":
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

        # Fractional Seed Replenishment (V020-C Keeper)
        current_seeds = self.state.seeds.get(target_crop, 0)
        if self.state.hour == 0 or current_seeds == 0:
            needed_seeds = min(DAILY_PLANT_CAP - current_seeds, len(empty_tiles))
            if needed_seeds > 0 and self.state.money > operating_reserve + (CROPS[target_crop]["seed"] * needed_seeds):
                if remaining_days - 1 >= CROPS.get(target_crop, {}).get("first_yield_day", 999):
                    buy_qty = min(self.state.money // CROPS[target_crop]["seed"], needed_seeds)
                    if buy_qty > 0:
                        self.tasks.append(Task("BUY_SEED", 50, kwargs={"product": target_crop, "quantity": buy_qty}))

        # Plant Target Seeds on Empty Tiles
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

        # Land Expansion Logic (V020-C Dynamic Operating Reserve)
        if len(empty_tiles) <= 5 and remaining_days >= 12:
            n_unlocked = len(self.state.unlocked_quads)
            land_prices = [1000, 2000, 4000]
            if 1 <= n_unlocked <= 3:
                next_cost = land_prices[n_unlocked - 1]
                if self.state.money > next_cost + operating_reserve:
                    self.tasks.append(Task("BUY_LAND", priority=100))

        self.tasks.sort(key=lambda t: t.priority)
        return self.tasks

# ==========================================
# 6. Task Allocator (Workload-Scaled Labor)
# ==========================================
class TaskAllocator:
    def __init__(self, state: GameState, econ: EconomicCalculator, tasks, strategy):
        self.state = state
        self.econ = econ
        self.tasks = tasks
        self.strategy = strategy
    
    def allocate(self):
        unassigned_field_tasks = [t for t in self.tasks if t.location is not None]
        active_workers = 1 + len(self.state.hands)
        remaining_turns = 24 - self.state.hour
        
        metrics = MetricsTracker.get()
        metrics["workers"]["max_active"] = max(metrics["workers"]["max_active"], active_workers)
        
        farm_tiles = self.state.my_farm.get("tiles", [])
        
        # Real recurring daily workload calculation
        unwatered_crops = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today", True))
        unfed_animals = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("animal") and not t.get("fed_today", True))
        uncared_animals = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("animal") and not t.get("cared_today", True))
        fert_available = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("fertilizer_available", False))
        harvest_ready = sum(1 for r in farm_tiles for t in r if isinstance(t, dict) and t.get("yield_units", 0) > 0)
        queued_plant_tasks = sum(1 for t in unassigned_field_tasks if t.action_type in ["PLANT", "BUILD_PASTURE", "BUILD_COOP", "PLACE"])
        
        units = [self.state.farmer] + self.state.hands
        min_start_dist = 0
        if unassigned_field_tasks:
            min_start_dist = min([abs(ux - tx) + abs(uy - ty) for ux, uy in units for t in unassigned_field_tasks for tx, ty in [t.location]], default=0)
            
        total_active_workload = unwatered_crops + (unfed_animals * 2) + uncared_animals + fert_available + harvest_ready + queued_plant_tasks
        required_actions = min_start_dist + (total_active_workload * 2) if total_active_workload > 0 else 0
        available_worker_actions = active_workers * remaining_turns
        labor_deficit = required_actions - available_worker_actions
        
        cost_of_next_hire = self.econ.get_hire_cost(self.state.hires_today)
        
        # Marginal ROI of adding a worker scales up to cost 34 when high animal workload deficit exists
        marginal_roi = min(35.0, max(self.strategy.config.worker_roi_threshold, (labor_deficit / 2.0) * 1.5))
        operating_reserve = self.strategy.config.cash_reserve + 320
        
        # Only hire if there is a real workload deficit, >3 turns remain today, and cash is protected
        if labor_deficit > 0 and remaining_turns > 3:
            if cost_of_next_hire <= marginal_roi:
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
        elif op == "BUY_ANIMAL": return 85000
        elif op == "BUY_PRODUCT": return 82000 # Wheat feed emergency
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
            if t.action_type in ["SELL", "BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "HIRE", "BUY_LAND"]:
                if t.action_type == "SELL":
                    market_actions.append(["SELL", t.kwargs["product"], t.kwargs["quantity"]])
                elif t.action_type == "BUY_SEED":
                    market_actions.append(["BUY_SEED", t.kwargs["product"], t.kwargs["quantity"]])
                elif t.action_type == "BUY_ANIMAL":
                    market_actions.append(["BUY_ANIMAL", t.kwargs["product"], t.kwargs["quantity"]])
                elif t.action_type == "BUY_PRODUCT":
                    market_actions.append(["BUY_PRODUCT", t.kwargs["product"], t.kwargs["quantity"]])
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
                    elif target.action_type == "PLACE":
                        action = ["PLACE", target.kwargs["item"]]
                    elif target.action_type in ["BUILD_PASTURE", "BUILD_COOP", "FEED", "CARE", "COLLECT_FERTILIZER", "WATER", "HARVEST"]:
                        action = [target.action_type]
                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
                    
            unit_actions.append(action)
            
        farmer_action = unit_actions[0] if unit_actions else ["PASS"]
        hands_actions = unit_actions[1:] if len(unit_actions) > 1 else []
        
        # Sort market actions by priority descending (high value sales and critical operations first)
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
