from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS, ANIMALS, PRODUCTS
import math
import os
import json
import collections
import numpy as np
from scipy.optimize import linear_sum_assignment

# ==========================================
# Metrics Tracking (Phase 3)
# ==========================================
# We use a global dict keyed by the seed (passed from experiments.py)
# so the data persists across the 720 steps.
_METRICS = collections.defaultdict(lambda: {
    "workers": {"hired": 0, "cost": 0, "active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0, "max_active": 0},
    "farmer": {"active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0},
    "economy": {"total_spending": 0, "total_revenue": 0, "seed_spending": 0, "worker_spending": 0},
    "crops": collections.defaultdict(lambda: {"planted": 0, "watered": 0, "harvested": 0, "deaths": 0}),
    "market": collections.defaultdict(lambda: {"sold": 0, "revenue": 0}),
    "water": {"generated": 0, "completed": 0, "misses": 0},
    "labor": {"required_sum": 0, "available_sum": 0, "deficit_sum": 0, "surplus_sum": 0, "cycles": 0},
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
                    
        # Track watering misses (end of day)
        if state.hour == 0 and state.day > 0:
            for loc, plant in m["_prev_plants"].items():
                if plant.get("consecutive_unwatered", 0) > 0 and not plant.get("watered_today", True):
                    m["water"]["misses"] += 1
                    
        m["_prev_plants"] = current_plants
    
    @staticmethod
    def save(player, step, final_money):
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        m = _METRICS[seed]
        m["economy"]["final_money"] = final_money
        
        # Calculate efficiencies
        total_worker_turns = m["workers"]["active_turns"] + m["workers"]["idle_turns"]
        useful = m["farmer"]["useful_actions"] + m["workers"]["useful_actions"]
        movement = m["farmer"]["movement_actions"] + m["workers"]["movement_actions"]
        
        m["efficiency"] = {
            "worker_utilization_pct": m["workers"]["active_turns"] / max(1, total_worker_turns) * 100,
            "farmer_utilization_pct": m["farmer"]["active_turns"] / max(1, m["farmer"]["active_turns"] + m["farmer"]["idle_turns"]) * 100,
            "useful_actions_total": useful,
            "movement_efficiency_pct": useful / max(1, useful + movement) * 100,
            "average_workers_day": m["workers"]["hired"] / 30.0,
            "max_workers": m["workers"]["max_active"]
        }
        
        # Save periodically to ensure metrics are not lost
        if step % 20 == 0 or step >= 710:
            os.makedirs("experiments/metrics", exist_ok=True)
            output = {k: dict(v) if isinstance(v, collections.defaultdict) else v for k, v in m.items() if k != "_prev_plants"}
            with open(f"experiments/metrics/game_{seed}_p{player}.json", "w") as f:
                json.dump(output, f, indent=2)

# ==========================================
# 1. Models & Task System
# ==========================================
class Task:
    def __init__(self, action_type, priority, location=None, kwargs=None):
        self.action_type = action_type # WATER, HARVEST, PLANT, BUY_SEED, SELL, HIRE
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
        if func_name == "linear":
            return x
        elif func_name == "sq":
            return x * x
        elif func_name == "sqrt":
            return math.sqrt(x)
        elif func_name == "log":
            return math.log(1.0 + x)
        elif func_name == "log10":
            return math.log10(1.0 + x)
        elif func_name == "hinge":
            if not T or T <= 0:
                return x
            u = x / T
            return u + 8.0 * max(0.0, u - 1.0)**2
        return x

    def get_price_at_inventory(self, product, inv):
        params = MARKET_PARAMS.get(product)
        if not params:
            return 1
            
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
                # Still gives $1 but doesn't add to inventory
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

    def marginal_roi_of_worker(self):
        return 15.0 

    def get_animal_roi(self, animal_name, historical_cost_per_action):
        animal_info = ANIMALS.get(animal_name)
        if not animal_info:
            return -999999, 0
            
        days_active = 30 - self.state.day
        if days_active < animal_info["first_yield_day"]:
            return -999999, 0
            
        production_cycles = (days_active - animal_info["first_yield_day"]) // animal_info["interval"] + 1
        yield_per_cycle = 1 + animal_info["interval"] # Assuming CARE every day adds `interval` units
        total_units = production_cycles * yield_per_cycle
        
        # We also get fertilizer every day
        total_fertilizer = days_active
        
        # Calculate expected revenue for primary product
        product = animal_info["product"]
        
        # Find existing pipeline (shed + unharvested + future production of existing animals)
        pipeline_qty = self.state.shed.get(product, 0)
        fert_pipeline_qty = self.state.shed.get("FERTILIZER", 0)
        
        existing_animals = 0
        farm_tiles = self.state.my_farm.get("tiles", [])
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict) and tile.get("kind") in ["COOP", "PASTURE"]:
                    if tile.get("animal") == animal_name:
                        existing_animals += 1
                        pipeline_qty += tile.get("yield_units", 0)
                    if "animal" in tile:
                        fert_pipeline_qty += tile.get("fertilizer_available", 0)
                        
        # Add future production of existing animals to the pipeline
        pipeline_qty += existing_animals * total_units
        fert_pipeline_qty += sum(1 for row in farm_tiles for t in row if isinstance(t, dict) and "animal" in t) * total_fertilizer
        
        current_inv = self.state.market.get("inventory", {}).get(product, 10000)
        sim_inv = current_inv + pipeline_qty
        expected_revenue = 0
        for i in range(total_units):
            p = self.get_price_at_inventory(product, sim_inv + i)
            expected_revenue += p
            
        # Add fertilizer revenue
        fert_inv = self.state.market.get("inventory", {}).get("FERTILIZER", 10000)
        fert_sim_inv = fert_inv + fert_pipeline_qty
        for i in range(total_fertilizer):
            p = self.get_price_at_inventory("FERTILIZER", fert_sim_inv + i)
            expected_revenue += p
            
        # Costs
        feed_cost = days_active * 25 # Assume WHEAT costs ~$25
        # worker actions: 3 per day (FEED, CARE, FERT) + harvests + build + place
        worker_actions = (days_active * 3) + production_cycles + 2
        worker_cost = worker_actions * historical_cost_per_action
        
        purchase_cost = animal_info["cost"]
        
        expected_net_profit = expected_revenue - feed_cost - worker_cost - purchase_cost
        profit_per_action = expected_net_profit / max(1, worker_actions)
        
        return profit_per_action, expected_net_profit 

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
                 expansion_policy="NONE",
                 animal_policy="NONE",
                 fertilizer_policy="NONE",
                 production_limit=25):
        self.crop_policy = crop_policy
        self.min_sell_price = min_sell_price
        self.sell_batch_size = sell_batch_size
        self.worker_roi_threshold = worker_roi_threshold
        self.cash_reserve = cash_reserve
        self.expansion_policy = expansion_policy
        self.animal_policy = animal_policy
        self.fertilizer_policy = fertilizer_policy
        self.production_limit = production_limit

class StrategicPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator, config: StrategyConfig = None):
        self.state = state
        self.econ = econ
        self.config = config or StrategyConfig()
        self.mode = "BALANCED" 
        self.reserve = self.config.cash_reserve 

# ==========================================
# 5. Daily Planner
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
        
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict):
                    if tile.get("kind") == "PLANT":
                        if not tile.get("watered_today", True):
                            self.tasks.append(Task("WATER", 10, (x, y)))
                        if tile.get("yield_units", 0) > 0:
                            if is_ready_to_harvest(tile.get("crop", ""), tile.get("planted_day", 0), self.state.day):
                                self.tasks.append(Task("HARVEST", 20, (x, y)))
                    elif tile.get("kind") in ["COOP", "PASTURE"]:
                        if "animal" in tile:
                            if not tile.get("fed_today", True):
                                # FEED consumes WHEAT from shed
                                if simulated_shed.get("WHEAT", 0) > 0:
                                    self.tasks.append(Task("FEED", 8, (x, y)))
                                    simulated_shed["WHEAT"] -= 1
                                else:
                                    # Need wheat to feed! Queue buy if we don't have tasks for it
                                    if not any(t.action_type == "BUY_PRODUCT" and t.kwargs.get("product") == "WHEAT" for t in self.tasks):
                                        self.tasks.append(Task("BUY_PRODUCT", 5, kwargs={"product": "WHEAT", "quantity": 1}))
                            if not tile.get("cared_today", True):
                                self.tasks.append(Task("CARE", 9, (x, y)))
                            if tile.get("yield_units", 0) > 0:
                                self.tasks.append(Task("HARVEST", 20, (x, y)))
                            if tile.get("fertilizer_available", False):
                                self.tasks.append(Task("COLLECT_FERTILIZER", 15, (x, y)))
                        else:
                            # Empty structure, try to place an animal
                            expected_animal = "GOOSE" if tile.get("kind") == "COOP" else "COW" # Could be sheep, we try whatever is in shed
                            for animal_type in ["GOOSE", "COW", "SHEEP"]:
                                if simulated_shed.get(animal_type, 0) > 0:
                                    # ensure structure matches
                                    if ANIMALS[animal_type]["structure"] == tile.get("kind"):
                                        self.tasks.append(Task("PLACE", 10, (x, y), {"item": animal_type}))
                                        simulated_shed[animal_type] -= 1
                                        break
                elif tile is None:
                    # Plant target crop if available, otherwise any available seed
                    planted_something = False
                    # target_crop is computed below, but we can't easily access it here without refactoring.
                    # Instead, we will just pick any available seed for now.
                    for available_crop, amount in simulated_seeds.items():
                        if amount > 0:
                            self.tasks.append(Task("PLANT", 30, (x, y), {"crop": available_crop}))
                            simulated_seeds[available_crop] -= 1
                            planted_something = True
                            break
        
        for product, qty in self.state.shed.items():
            if qty > 0:
                # We want to sell up to maximum we can without hitting price floor
                # The market accepts max 10 orders per turn overall, so we shouldn't submit small orders
                # Let's find how many we can sell before marginal price drops to 1
                current_inv = self.state.market.get("inventory", {}).get(product, 10000)
                sell_qty = 0
                for i in range(qty):
                    p = self.econ.get_price_at_inventory(product, current_inv + i)
                    if p > self.strategy.config.min_sell_price:
                        sell_qty += 1
                    else:
                        break
                
                # If we can sell, queue it. Limit to batch size to not over-saturate a single turn
                if sell_qty > 0:
                    sell_qty = min(sell_qty, self.strategy.config.sell_batch_size)
                    self.tasks.append(Task("SELL", 5, kwargs={"product": product, "quantity": sell_qty}))
                    
        # Crop Diversification Logic (V004-B)
        best_crop = self.strategy.config.crop_policy
        best_profit_per_action = -999999
        
        crop_actions = {
            "WHEAT": 5, "CARROT": 4, "TOMATO": 15, "STRAWBERRY": 20, "MELON": 12
        }
        crop_max_yield = {
            "WHEAT": 6, "CARROT": 4, "TOMATO": 16, "STRAWBERRY": 16, "MELON": 6
        }
        
        metrics = MetricsTracker.get()
        useful_actions = metrics["workers"]["useful_actions"] + metrics["farmer"]["useful_actions"]
        if useful_actions == 0:
            historical_cost_per_action = 1.0 / 24.0
        else:
            historical_cost_per_action = metrics["economy"]["worker_spending"] / useful_actions
            
        farm_tiles = self.state.my_farm.get("tiles", [])
            
        for crop_name in crop_actions.keys():
            seed_cost = CROPS.get(crop_name, {}).get("seed", 999)
            
            # Count pipeline (shed + planted)
            planted_count = sum(1 for y in range(self.state.board_size) for x in range(self.state.board_size) 
                              if isinstance(farm_tiles[y][x], dict) and farm_tiles[y][x].get("kind") == "PLANT" and farm_tiles[y][x].get("crop") == crop_name)
            
            pipeline_qty = self.state.shed.get(crop_name, 0) + (planted_count + self.state.seeds.get(crop_name, 0)) * crop_max_yield[crop_name]
            
            # 1. Expected Revenue (of the new crop)
            current_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
            sim_inv = current_inv + pipeline_qty
            expected_revenue = 0
            for i in range(crop_max_yield[crop_name]):
                p = self.econ.get_price_at_inventory(crop_name, sim_inv + i)
                expected_revenue += p
                
            # 2. Expected Worker Cost
            expected_worker_cost = crop_actions[crop_name] * historical_cost_per_action
            
            # 3. Expected Market Impact 
            # In Kaggriculture, market processes 1 unit at a time. The existing pipeline's value
            # is unchanged by the new crop because the new crop is sold LAST.
            expected_market_impact = 0 
            
            # 4. Expected Crop Loss
            planted = metrics["crops"][crop_name]["planted"]
            deaths = metrics["crops"][crop_name]["deaths"]
            death_rate = (deaths / planted) if planted > 0 else 0
            expected_crop_loss = expected_revenue * death_rate
            
            expected_net_profit = expected_revenue - seed_cost - expected_worker_cost - expected_market_impact - expected_crop_loss
            profit_per_action = expected_net_profit / crop_actions[crop_name]
            
            if profit_per_action > best_profit_per_action:
                best_profit_per_action = profit_per_action
                best_crop = crop_name
                
        target_crop = best_crop
        
        # Animal Diversification Logic (V005-C - Best Animal Only)
        best_animal = "SHEEP"
        prof_per_action, net_prof = self.econ.get_animal_roi(best_animal, historical_cost_per_action)
                
        # Compare vs 0 instead of crops
        if prof_per_action > 0:
            if self.state.shed.get(best_animal, 0) == 0 and self.state.money > self.strategy.config.cash_reserve + ANIMALS[best_animal]["cost"]:
                # Check if we have an empty matching structure first, if not, we must build one
                structure_type = ANIMALS[best_animal]["structure"]
                empty_structures = sum(1 for y in range(self.state.board_size) for x in range(self.state.board_size) 
                                      if isinstance(farm_tiles[y][x], dict) and farm_tiles[y][x].get("kind") == structure_type and "animal" not in farm_tiles[y][x])
                
                # Check how many we are already building
                building_tasks = sum(1 for t in self.tasks if t.action_type == f"BUILD_{structure_type}")
                
                # If we don't have enough structures, queue a build task
                if empty_structures + building_tasks == 0:
                    # Find empty tile to build
                    for y in range(self.state.board_size):
                        for x in range(self.state.board_size):
                            if farm_tiles[y][x] is None and not any(t.location == (x,y) for t in self.tasks):
                                self.tasks.append(Task(f"BUILD_{structure_type}", 40, (x, y)))
                                break
                                
                # Buy the animal
                self.tasks.append(Task("BUY_ANIMAL", 50, kwargs={"product": best_animal, "quantity": 1}))
        
        self.tasks.sort(key=lambda t: t.priority)
        return self.tasks

# ==========================================
# 6. Task Allocator
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
        metrics["labor"]["cycles"] += 1
        
        # Calculate dynamic labor requirements for the rest of the day
        empty_unlocked = 0
        farm_tiles = self.state.my_farm.get("tiles", [])
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                if farm_tiles[y][x] is None:
                    empty_unlocked += 1
                    
        queued_plant_tasks = sum(1 for t in unassigned_field_tasks if t.action_type == "PLANT")
        uninstantiated_plant_tasks = max(0, empty_unlocked - queued_plant_tasks)
        
        # Exact workload calculation based on routing approximations
        # Moving to first task takes dist, then execution takes 1.
        # Moving to next task takes ~1, execution takes 1 -> 2 actions per subsequent task.
        # So total workload for N tasks is ~dist_to_first + 2 * (N - 1) + 1 
        # which simplifies to dist_to_first + 2 * N - 1
        # For simplicity and slight conservative padding, we use dist_to_first + 2 * N
        units = [self.state.farmer] + self.state.hands
        min_start_dist = 0
        if unassigned_field_tasks or uninstantiated_plant_tasks > 0:
            # Assume tasks are distributed, we just find minimum distance from any worker to any existing task.
            # If no existing tasks, we are just planting empty tiles, we use shed distance (since new seeds come from shed)
            if unassigned_field_tasks:
                min_start_dist = min([abs(ux - tx) + abs(uy - ty) for ux, uy in units for t in unassigned_field_tasks for tx, ty in [t.location]], default=0)
            else:
                # Shed is at 4, 4
                min_start_dist = min([abs(ux - 4) + abs(uy - 4) for ux, uy in units], default=0)
                
        total_tasks = len(unassigned_field_tasks) + uninstantiated_plant_tasks
        required_actions = min_start_dist + (total_tasks * 2) if total_tasks > 0 else 0
        
        available_worker_actions = active_workers * remaining_turns
        
        labor_deficit = required_actions - available_worker_actions
        labor_surplus = available_worker_actions - required_actions
        
        # Track metrics
        metrics["labor"]["required_sum"] += required_actions
        metrics["labor"]["available_sum"] += available_worker_actions
        metrics["labor"]["deficit_sum"] += max(0, labor_deficit)
        metrics["labor"]["surplus_sum"] += max(0, labor_surplus)
        
        cost_of_next_hire = self.econ.get_hire_cost(self.state.hires_today)
        expected_roi = self.strategy.config.worker_roi_threshold
        
        # Only hire if there is a deficit, remaining turns make it worthwhile (>3), and we have the ROI/funds.
        if labor_deficit > 0 and remaining_turns > 3:
            if expected_roi > cost_of_next_hire:
                if self.state.money > cost_of_next_hire + self.strategy.config.cash_reserve:
                    self.tasks.append(Task("HIRE", 1))

        return {}

# ==========================================
# 7. Action Executor
# ==========================================
class ActionExecutor:
    def __init__(self, state: GameState, econ: EconomicCalculator):
        self.state = state
        self.econ = econ
        self.metrics = MetricsTracker.get()
        
    def step_toward(self, fx, fy, tx, ty):
        # ponytail: The grid has no hard obstacles (all tiles are passable), so greedy Manhattan L-routing 
        # is optimal and identical in length to BFS. Kept step_toward() instead of building a full BFS graph search.
        if fx > tx: return "WEST"
        if fx < tx: return "EAST"
        if fy > ty: return "NORTH"
        if fy < ty: return "SOUTH"
        return "PASS"
    
    def execute(self, tasks, assignments):
        market_actions = []
        field_tasks = []
        
        for t in tasks:
            if t.action_type in ["SELL", "BUY_SEED", "HIRE", "BUY_PRODUCT", "BUY_ANIMAL"]:
                if t.action_type == "SELL":
                    market_actions.append(["SELL", t.kwargs["product"], t.kwargs["quantity"]])
                    # Track metrics
                    self.metrics["market"][t.kwargs["product"]]["sold"] += t.kwargs["quantity"]
                    current_price = self.state.market.get("prices", {}).get(t.kwargs["product"], 1)
                    # Simplified tracking of revenue assuming no immediate price drop within the same order
                    self.metrics["market"][t.kwargs["product"]]["revenue"] += current_price * t.kwargs["quantity"]
                    self.metrics["economy"]["total_revenue"] += current_price * t.kwargs["quantity"]
                elif t.action_type == "BUY_SEED":
                    market_actions.append(["BUY_SEED", t.kwargs["product"], t.kwargs["quantity"]])
                    # Track metrics
                    cost = CROPS.get(t.kwargs["product"], {}).get("seed", 0) * t.kwargs["quantity"]
                    self.metrics["economy"]["seed_spending"] += cost
                    self.metrics["economy"]["total_spending"] += cost
                elif t.action_type == "BUY_ANIMAL":
                    market_actions.append(["BUY_ANIMAL", t.kwargs["product"], t.kwargs["quantity"]])
                    cost = ANIMALS.get(t.kwargs["product"], {}).get("cost", 0) * t.kwargs["quantity"]
                    self.metrics["economy"]["total_spending"] += cost
                elif t.action_type == "BUY_PRODUCT":
                    market_actions.append(["BUY_PRODUCT", t.kwargs["product"], t.kwargs["quantity"]])
                    current_price = self.state.market.get("prices", {}).get(t.kwargs["product"], 1)
                    cost = current_price * t.kwargs["quantity"]
                    self.metrics["economy"]["total_spending"] += cost
                elif t.action_type == "HIRE":
                    market_actions.append(["HIRE"])
                    cost = self.econ.get_hire_cost(self.state.hires_today)
                    self.metrics["workers"]["hired"] += 1
                    self.metrics["workers"]["cost"] += cost
                    self.metrics["economy"]["worker_spending"] += cost
                    self.metrics["economy"]["total_spending"] += cost
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
                    
                    # Compute a cost value for this worker-task pair
                    cost = 0
                    
                    # 1. Hard Constraints (Urgent tasks that could expire)
                    # For WATER, the plant dies 2 days after planted if not watered. 
                    # If dist > remaining_time, it's impossible.
                    # As a simpler heuristic for the baseline Strategy's priority:
                    # Priority >= 1000 means it's an urgent watering task.
                    if target.priority >= 1000:
                        # Massive negative cost ensures this task is matched to SOME worker
                        cost = -1000000 + dist * 10
                    else:
                        # Soft optimization: minimize distance, maximize economic value (which drives priority)
                        cost = (dist * 10) - target.priority

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
                        self.metrics["crops"][target.kwargs["crop"]]["planted"] += 1
                    elif target.action_type == "PLACE":
                        action = ["PLACE", target.kwargs["item"]]
                    else:
                        action = [target.action_type]
                        if target.action_type == "WATER":
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                self.metrics["crops"][tile["crop"]]["watered"] += 1
                        elif target.action_type == "HARVEST":
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                self.metrics["crops"][tile["crop"]]["harvested"] += 1
                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
                    
                if "assignments_count" not in self.metrics["workers"]:
                    self.metrics["workers"]["assignments_count"] = 0
                    self.metrics["workers"]["total_assignment_distance"] = 0
                self.metrics["workers"]["assignments_count"] += 1
                self.metrics["workers"]["total_assignment_distance"] += abs(ux - tx) + abs(uy - ty)
                
            unit_actions.append(action)
            
            # Track worker/farmer turns
            is_farmer = (ui == 0)
            target_metric = self.metrics["farmer"] if is_farmer else self.metrics["workers"]
            if action[0] == "PASS":
                target_metric["idle_turns"] += 1
            elif action[0] in ["NORTH", "SOUTH", "EAST", "WEST"]:
                target_metric["active_turns"] += 1
                target_metric["movement_actions"] += 1
            else:
                target_metric["active_turns"] += 1
                target_metric["useful_actions"] += 1
                
        farmer_action = unit_actions[0] if unit_actions else ["PASS"]
        hands_actions = unit_actions[1:] if len(unit_actions) > 1 else []
        
        # Enforce limits
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
        
        MetricsTracker.save(state.player, state.step, state.money)
        return actions
        
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
