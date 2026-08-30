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
        "state_parsing": 0.0,
        "economic_calc": 0.0,
        "strategic_planning": 0.0,
        "daily_planning": 0.0,
        "task_allocation": 0.0,
        "action_execution": 0.0,
        "metrics_tracking": 0.0,
        "total_turn": 0.0,
        "calls": 0
    }
})

class MetricsTracker:
    current_seed = "default"
    
    @classmethod
    def get(cls):
        return _METRICS[cls.current_seed]

    @classmethod
    def track_plants(cls, state):
        metrics = cls.get()
        if not state.my_farm:
            return
        tiles = state.my_farm.get("tiles", [])
        for r in range(state.board_size):
            for c in range(state.board_size):
                tile = tiles[r][c]
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    crop_name = tile.get("crop")
                    consecutive_unwatered = tile.get("consecutive_unwatered", 0)
                    if consecutive_unwatered == 2:
                        metrics["crops"][crop_name]["deaths"] += 1
                        
    @classmethod
    def save(cls, player, step, money, shed, actions=None, day=0):
        m = cls.get()
        if actions:
            if "market" in actions:
                for ma in actions["market"]:
                    if len(ma) > 0:
                        op = ma[0]
                        if op == "BUY_SEED":
                            crop = ma[1]
                            qty = ma[2]
                            cost = CROPS[crop]["seed"] * qty
                            m["economy"]["total_spending"] += cost
                            m["economy"]["seed_spending"] += cost
                            if crop in ["TOMATO", "STRAWBERRY", "MELON"]:
                                pass
                            else:
                                m["v018"]["filler_seed_cost"] += cost
                        elif op == "HIRE":
                            pass
            
            if "farmer" in actions and actions["farmer"]:
                f_act = actions["farmer"][0]
                if f_act in ["NORTH", "SOUTH", "EAST", "WEST"]:
                    m["farmer"]["movement_actions"] += 1
                elif f_act == "PASS":
                    m["farmer"]["idle_turns"] += 1
                else:
                    m["farmer"]["useful_actions"] += 1
                m["farmer"]["active_turns"] += 1

            if "hands" in actions and actions["hands"]:
                for h_act_list in actions["hands"]:
                    if h_act_list:
                        h_act = h_act_list[0]
                        if h_act in ["NORTH", "SOUTH", "EAST", "WEST"]:
                            m["workers"]["movement_actions"] += 1
                        elif h_act == "PASS":
                            m["workers"]["idle_turns"] += 1
                        else:
                            m["workers"]["useful_actions"] += 1
                        m["workers"]["active_turns"] += 1

        if step == 719:
            try:
                data = {
                    "player": player,
                    "final_money": money,
                    "final_shed": shed,
                    "workers": m["workers"],
                    "farmer": m["farmer"],
                    "economy": m["economy"],
                    "crops": {k: dict(v) for k, v in m["crops"].items()},
                    "market": {k: dict(v) for k, v in m["market"].items()},
                    "water": m["water"],
                    "labor": m["labor"],
                    "spatial": m["spatial"],
                    "v018": m["v018"],
                    "timing": m["timing"]
                }
                
                # Write to seed-specific json in experiments/data/
                os.makedirs("experiments/data", exist_ok=True)
                with open(f"experiments/data/seed_{cls.current_seed}_p{player}.json", "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

# ==========================================
# 1. Game State Parser
# ==========================================
class GameState:
    def __init__(self, obs):
        self.raw_obs = obs
        self.step = obs.get("step", 0)
        self.day = obs.get("day", 0)
        self.hour = obs.get("hour", 0)
        self.player = obs.get("player", 0)
        
        self.farms = obs.get("farms", [])
        self.my_farm = self.farms[self.player] if len(self.farms) > self.player else {}
        self.opp_farm = self.farms[1 - self.player] if len(self.farms) > (1 - self.player) else {}
        
        self.money = self.my_farm.get("money", 0)
        self.farmer = self.my_farm.get("farmer", [0, 0])
        self.hands = self.my_farm.get("hands", [])
        self.unlocked_quadrants = self.my_farm.get("unlocked_quadrants", ["NW"])
        self.hires_today = self.my_farm.get("hires_today", 0)
        
        self.private = obs.get("private", {})
        self.shed = self.private.get("shed", {})
        self.seeds = self.private.get("seeds", {})
        self.inventories = self.private.get("inventories", [])
        
        self.market = obs.get("market", {})
        self.town = obs.get("town", {})
        self.board_size = 10
        
    def get_tile(self, x, y):
        tiles = self.my_farm.get("tiles", [])
        if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
            return tiles[y][x]
        return "LOCKED"

MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 1500, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
    "CARROT": {"base": 35, "I0": 10000, "T": 1150, "below_func": "hinge", "below_target": 0.60, "above_func": "log", "above_target": 0.20},
    "TOMATO": {"base": 70, "I0": 10000, "T": 650, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.20},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 400, "below_func": "sq", "below_target": 0.80, "above_func": "sq", "above_target": 3.20},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40}
}

# ==========================================
# 2. Economic Calculator
# ==========================================
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
        
    def expected_sale_revenue(self, crop: str, quantity: int) -> float:
        current_inv = self.state.market.get("inventory", {}).get(crop, 10000)
        current_price = self.get_price_at_inventory(crop, current_inv)
        marginal_inv = current_inv + quantity
        future_price = self.get_price_at_inventory(crop, marginal_inv)
        avg_price = (current_price + future_price) / 2.0
        return quantity * avg_price

    def get_forward_marginal_price(self, crop_name: str, additional_units: int = 1) -> float:
        current_market_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
        
        my_shed = self.state.shed.get(crop_name, 0)
        my_planted = 0
        opp_planted = 0
        
        my_tiles = self.state.my_farm.get("tiles", [])
        for r in range(self.state.board_size):
            for c in range(self.state.board_size):
                t = my_tiles[r][c]
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop_name:
                    my_planted += t.get("yield_units", 1)
                    
        opp_tiles = self.state.opp_farm.get("tiles", [])
        for r in range(self.state.board_size):
            for c in range(self.state.board_size):
                t = opp_tiles[r][c]
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop_name:
                    opp_planted += t.get("yield_units", 1)
                    
        unlocked_shops = self.state.town.get("unlocked_shops", [])
        shop_count = sum(1 for s in unlocked_shops if crop_name in s or "ALL" in s)
        days_left = max(0, 30 - self.state.day)
        total_drain = (shop_count * 6 + 1) * days_left
        
        projected_inv = current_market_inv + my_shed + my_planted + opp_planted - total_drain + additional_units
        return self.get_price_at_inventory(crop_name, projected_inv)

# ==========================================
# 3. Strategy Configuration
# ==========================================
class StrategyConfig:
    def __init__(self):
        self.labor_buffer_ratio = 1.2
        self.worker_roi_threshold = 20.0
        self.cash_reserve = 400
        self.planning_horizon = 30

# ==========================================
# 4. Strategic Planner
# ==========================================
class StrategicPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator):
        self.state = state
        self.econ = econ
        self.config = StrategyConfig()
        
    def evaluate_target_crops(self):
        # V020-B: Crop lifecycle & market aware ranking
        days_left = 30 - self.state.day
        evaluations = {}
        
        for crop_name, info in CROPS.items():
            first_yield = info.get("first_yield_day", 999)
            if days_left - 1 < first_yield:
                continue # Impossible to mature in time
                
            seed_cost = info["seed"]
            
            # Achievable yields
            if crop_name == "MELON":
                yield_units = 6 if (days_left - 1 >= 12) else 3
            elif crop_name == "CARROT":
                yield_units = 3
            elif crop_name == "WHEAT":
                yield_units = 4
            elif crop_name in ["TOMATO", "STRAWBERRY"]:
                yield_units = 4
            else:
                yield_units = 3
                
            forward_price = self.econ.get_forward_marginal_price(crop_name, yield_units)
            revenue = yield_units * forward_price
            net_profit = revenue - seed_cost
            
            crop_actions = {"WHEAT": 5, "CARROT": 5, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 12}
            actions = crop_actions.get(crop_name, 6)
            profit_per_action = net_profit / actions
            
            evaluations[crop_name] = {
                "net_profit": net_profit,
                "profit_per_action": profit_per_action,
                "forward_price": forward_price
            }
            
        return evaluations

# ==========================================
# 5. Daily Planner
# ==========================================
class Task:
    def __init__(self, action_type, priority, location=None, kwargs=None):
        self.action_type = action_type
        self.priority = priority
        self.location = location
        self.kwargs = kwargs or {}

class DailyPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator, strategy: StrategicPlanner):
        self.state = state
        self.econ = econ
        self.strategy = strategy
        self.tasks = []
        
    def plan_tasks(self):
        self.tasks = []
        farm_tiles = self.state.my_farm.get("tiles", [])
        
        # 1. Market Selling Tasks
        for product, qty in self.state.shed.items():
            if qty > 0:
                self.tasks.append(Task("SELL", 10, kwargs={"product": product, "quantity": qty}))
                
        # 2. Plant Maintenance Tasks
        empty_tiles = []
        existing_crops = []
        simulated_seeds = dict(self.state.seeds)
        simulated_shed = dict(self.state.shed)
        
        days_left = 30 - self.state.day
        is_endgame = (self.state.day >= 28)
        
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict):
                    kind = tile.get("kind")
                    if kind == "PLANT":
                        existing_crops.append((x, y))
                        crop_name = tile.get("crop")
                        crop_info = CROPS.get(crop_name, {})
                        age = self.state.day - tile.get("planted_day", 0)
                        first_yield = crop_info.get("first_yield_day", 999)
                        max_yield = crop_info.get("max_yield_day", 999)
                        yield_units = tile.get("yield_units", 0)
                        watered = tile.get("watered_today", False)
                        
                        # Priority 1: HARVEST if mature
                        # On Days 28-29, harvest immediately if ANY yield exists
                        if is_endgame and yield_units > 0:
                            self.tasks.append(Task("HARVEST", 5, (x, y)))
                        elif age >= first_yield and yield_units > 0:
                            if age >= max_yield or age >= (first_yield + 2):
                                self.tasks.append(Task("HARVEST", 5, (x, y)))
                            elif is_endgame:
                                self.tasks.append(Task("HARVEST", 5, (x, y)))
                                
                        # Priority 2: WATER if unwatered and crop can mature before season end
                        if not watered:
                            can_mature = (age + (30 - self.state.day) >= first_yield)
                            if can_mature or yield_units > 0:
                                # High priority watering
                                self.tasks.append(Task("WATER", 15, (x, y)))
                            elif not is_endgame:
                                self.tasks.append(Task("WATER", 25, (x, y)))
                                
                    elif kind == "WEED":
                        # Clear weeds if space constrained
                        if not is_endgame:
                            self.tasks.append(Task("DIG", 60, (x, y)))
                elif tile is None:
                    empty_tiles.append((x, y))
                    
        # --- Batch Cap & Planting ---
        DAILY_PLANT_CAP = 4
        
        # Determine target crop
        crop_evals = self.strategy.evaluate_target_crops()
        best_crop = "MELON"
        best_ppa = -999
        
        # Preference: Melon early (Days 0-18), Carrot mid-late (Days 19-25), Wheat endgame (Days 25-27)
        if self.state.day <= 18 and "MELON" in crop_evals:
            best_crop = "MELON"
            best_ppa = crop_evals["MELON"]["profit_per_action"]
        elif self.state.day <= 25 and "CARROT" in crop_evals:
            best_crop = "CARROT"
            best_ppa = crop_evals["CARROT"]["profit_per_action"]
        elif self.state.day <= 27 and "WHEAT" in crop_evals:
            best_crop = "WHEAT"
            best_ppa = crop_evals["WHEAT"]["profit_per_action"]
        elif crop_evals:
            # Fallback to highest profit per action
            for c, ev in crop_evals.items():
                if ev["profit_per_action"] > best_ppa:
                    best_ppa = ev["profit_per_action"]
                    best_crop = c
                    
        # Buy Seeds (V020-B Fix: Avoid Fractional Seed Stall)
        target_crop = best_crop
        if not is_endgame and target_crop in CROPS:
            curr_seeds = self.state.seeds.get(target_crop, 0)
            seed_price = CROPS[target_crop]["seed"]
            # Buy enough to plant up to DAILY_PLANT_CAP if we have empty tiles
            needed_seeds = max(0, min(DAILY_PLANT_CAP - curr_seeds, len(empty_tiles) - curr_seeds))
            if needed_seeds > 0 and self.state.money > self.strategy.config.cash_reserve + (seed_price * needed_seeds):
                self.tasks.append(Task("BUY_SEED", 40, kwargs={"product": target_crop, "quantity": needed_seeds}))
                simulated_seeds[target_crop] = curr_seeds + needed_seeds
                
        # Limit planting to batch cap
        for crop in list(simulated_seeds.keys()):
            if simulated_seeds[crop] > DAILY_PLANT_CAP:
                simulated_seeds[crop] = DAILY_PLANT_CAP
                
        total_seeds_to_plant = sum(simulated_seeds.values())
        
        # Spatial placement
        while total_seeds_to_plant > 0 and empty_tiles and not is_endgame:
            seed_to_plant = None
            for c, amt in simulated_seeds.items():
                if amt > 0:
                    seed_to_plant = c
                    break
            if not seed_to_plant:
                break
                
            # Pick closest empty tile to existing crops or farmer
            fx, fy = self.state.farmer
            best_tile = None
            best_dist = 9999
            for (ex, ey) in empty_tiles:
                dist = abs(ex - fx) + abs(ey - fy)
                if existing_crops:
                    min_crop_dist = min(abs(ex - cx) + abs(ey - cy) for cx, cy in existing_crops)
                    cost = min_crop_dist * 2 + dist
                else:
                    cost = dist
                if cost < best_dist:
                    best_dist = cost
                    best_tile = (ex, ey)
                    
            if best_tile:
                empty_tiles.remove(best_tile)
                self.tasks.append(Task("PLANT", 30, best_tile, {"crop": seed_to_plant}))
                simulated_seeds[seed_to_plant] -= 1
                total_seeds_to_plant -= 1
                existing_crops.append(best_tile)
            else:
                break
                
        # --- Land Expansion (V020-B Fix: Lower reserve threshold for NE quadrant) ---
        if len(empty_tiles) <= 5 and not is_endgame:
            unlocked = self.state.my_farm.get("unlocked_quadrants", [])
            n_unlocked = len(unlocked)
            land_prices = [1000, 2000, 4000]
            if 1 <= n_unlocked <= 3:
                next_cost = land_prices[n_unlocked - 1]
                # Lower reserve threshold to $800 above land price so quadrant 2 (NE) unlocks reliably
                if self.state.money > next_cost + 800:
                    self.tasks.append(Task("BUY_LAND", priority=90))
                    
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
        
        # Workload calculation
        workload = len(unassigned_field_tasks) * 2
        capacity = active_workers * remaining_turns
        labor_deficit = workload - capacity
        
        # Hiring logic
        cost_of_next_hire = 1
        hires = self.state.hires_today
        if hires > 0:
            a, b = 1, 1
            for _ in range(hires):
                a, b = b, a + b
            cost_of_next_hire = a
            
        if labor_deficit > 0 and remaining_turns > 4 and self.state.day < 28:
            if cost_of_next_hire < self.strategy.config.worker_roi_threshold:
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
        if fx > tx: return "WEST"
        if fx < tx: return "EAST"
        if fy > ty: return "NORTH"
        if fy < ty: return "SOUTH"
        return "PASS"
        
    def execute(self, tasks, assignments):
        metrics = self.metrics
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
                
        # Limit market actions to 10
        market_actions = market_actions[:10]
        
        units = [self.state.farmer] + self.state.hands
        num_units = len(units)
        assigned_targets = [None] * num_units
        
        if field_tasks:
            cost_matrix = np.zeros((num_units, len(field_tasks)))
            for i, (ux, uy) in enumerate(units):
                for j, target in enumerate(field_tasks):
                    tx, ty = target.location
                    dist = abs(ux - tx) + abs(uy - ty)
                    cost = (dist * 10) + target.priority
                    cost_matrix[i, j] = cost
                    
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            for i, j in zip(row_ind, col_ind):
                assigned_targets[i] = field_tasks[j]
                
        actions = []
        for ui, (ux, uy) in enumerate(units):
            action = ["PASS"]
            target = assigned_targets[ui]
            if target is not None:
                tx, ty = target.location
                if ux == tx and uy == ty:
                    if target.action_type == "PLANT":
                        action = ["PLANT", target.kwargs["crop"]]
                    else:
                        action = [target.action_type]
                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
            actions.append(action)
            
        farmer_action = actions[0] if actions else ["PASS"]
        hands_actions = actions[1:] if len(actions) > 1 else []
        
        return {
            "farmer": farmer_action,
            "hands": hands_actions,
            "market": market_actions
        }

# ==========================================
# Main Entry Point
# ==========================================
def agent(obs):
    try:
        state = GameState(obs)
        if not state.my_farm:
            return {"farmer": ["PASS"], "hands": [], "market": []}
            
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        tasks = planner.plan_tasks()
        
        allocator = TaskAllocator(state, econ, tasks, strategy)
        assignments = allocator.allocate()
        
        executor = ActionExecutor(state, econ)
        return executor.execute(tasks, assignments)
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
