from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
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
                    
        # Track watering misses (end of day)
        if state.hour == 0 and state.day > 0:
            for loc, plant in m["_prev_plants"].items():
                if plant.get("consecutive_unwatered", 0) > 0 and not plant.get("watered_today", True):
                    m["water"]["misses"] += 1
                    
        # Track spatial metrics
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
            
            # Count isolated
            isolated = 0
            for p in plants:
                has_neighbor = False
                for other in plants:
                    if p != other and abs(p[0] - other[0]) + abs(p[1] - other[1]) == 1:
                        has_neighbor = True
                        break
                if not has_neighbor:
                    isolated += 1
            m["spatial"]["isolated_clusters"] += isolated
            
            # Clustering metrics (distance <= 2)
            clusters = []
            visited = set()
            for p in plants:
                if p not in visited:
                    cluster = set()
                    q = [p]
                    while q:
                        curr = q.pop(0)
                        if curr not in visited:
                            visited.add(curr)
                            cluster.add(curr)
                            for other in plants:
                                if other not in visited and (abs(curr[0] - other[0]) + abs(curr[1] - other[1])) <= 2:
                                    q.append(other)
                    clusters.append(cluster)
            
            m["spatial"]["cluster_count_sum"] += len(clusters)
            cluster_sizes = [len(c) for c in clusters]
            m["spatial"]["mean_cluster_size_sum"] += sum(cluster_sizes) / len(clusters)
            m["spatial"]["max_cluster_size_sum"] += max(cluster_sizes)
            
            if len(clusters) > 1:
                inter_dist = 0
                inter_pairs = 0
                for i in range(len(clusters)):
                    for j in range(i+1, len(clusters)):
                        c1, c2 = clusters[i], clusters[j]
                        x1 = sum(p[0] for p in c1)/len(c1)
                        y1 = sum(p[1] for p in c1)/len(c1)
                        x2 = sum(p[0] for p in c2)/len(c2)
                        y2 = sum(p[1] for p in c2)/len(c2)
                        inter_dist += abs(x1-x2) + abs(y1-y2)
                        inter_pairs += 1
                m["spatial"]["inter_cluster_dist_sum"] += inter_dist / inter_pairs
                
            # Future task density (estimate active tasks around each crop)
            task_density = 0
            for loc, plant in current_plants.items():
                # rough estimate of future tasks: 1 per day alive
                crop_name = plant.get("crop", "WHEAT")
                # default approx
                future_tasks = 4
                if crop_name == "MELON": future_tasks = 5
                
                # count neighbors within dist 3
                neighbors = sum(1 for p in plants if p != loc and abs(p[0] - loc[0]) + abs(p[1] - loc[1]) <= 3)
                task_density += future_tasks * neighbors
            m["spatial"]["future_task_density_sum"] += task_density / len(plants)
                    
        m["_prev_plants"] = current_plants
    
    @staticmethod
    def save(player, step, final_money, shed=None, actions=None, day=None):
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        m = _METRICS[seed]
        m["economy"]["final_money"] = final_money
        if shed:
            m["final_shed"] = shed
            
        if actions and day is not None:
            # Track market actions
            for market_action in actions.get("market", []):
                if market_action and market_action[0] == "BUY_SEED":
                    crop = market_action[1]
                    n = int(market_action[2]) if len(market_action) > 2 else 1
                    m["timing"]["seeds_purchased_by_crop"][crop] += n
                    if day >= 20:
                        m["timing"]["late_season_seeds_purchased"] += n
                        
                    crop_info = CROPS.get(crop, {})
                    first_yield = crop_info.get("first_yield_day", 999)
                    if day > 29 - first_yield:
                        m["timing"]["seeds_purchased_after_profitable"] += n
                        
                elif market_action and market_action[0] == "SELL":
                    item = market_action[1]
                    n = int(market_action[2]) if len(market_action) > 2 else 1
                    pass 

            # Track planting actions
            units = []
            if "farmer" in actions and actions["farmer"]:
                units.append(actions["farmer"])
            for h in actions.get("hands", []):
                if h: units.append(h)
                
            for u_action in units:
                if u_action[0] == "PLANT":
                    crop = u_action[1]
                    m["timing"]["plants_by_crop"][crop].append(day)
                    if day >= 20:
                        m["timing"]["late_season_crops_planted"] += 1
        
        # Calculate efficiencies
        total_worker_turns = m["workers"]["active_turns"] + m["workers"]["idle_turns"]
        useful = m["farmer"]["useful_actions"] + m["workers"]["useful_actions"]
        total_movement = m["farmer"]["movement_actions"] + m["workers"]["movement_actions"]
        
        m["efficiency"] = {
            "worker_utilization_pct": m["workers"]["active_turns"] / max(1, total_worker_turns) * 100,
            "farmer_utilization_pct": m["farmer"]["active_turns"] / max(1, m["farmer"]["active_turns"] + m["farmer"]["idle_turns"]) * 100,
            "useful_actions_total": useful,
            "movement_efficiency_pct": useful / max(1, useful + total_movement) * 100,
            "average_workers_day": m["workers"]["hired"] / 30.0,
            "max_workers": m["workers"]["max_active"],
            "spatial_fragmentation": m["spatial"]["fragmentation_sum"] / max(1, m["spatial"]["samples"]),
            "average_isolated": m["spatial"]["isolated_clusters"] / max(1, m["spatial"]["samples"]),
            "cluster_count": m["spatial"]["cluster_count_sum"] / max(1, m["spatial"]["samples"]),
            "mean_cluster_size": m["spatial"]["mean_cluster_size_sum"] / max(1, m["spatial"]["samples"]),
            "max_cluster_size": m["spatial"]["max_cluster_size_sum"] / max(1, m["spatial"]["samples"]),
            "inter_cluster_distance": m["spatial"]["inter_cluster_dist_sum"] / max(1, m["spatial"]["samples"]),
            "future_task_density": m["spatial"]["future_task_density_sum"] / max(1, m["spatial"]["samples"])
        }
        
        # Save periodically to ensure metrics are not lost
        if step % 20 == 0 or step >= 710:
            if step >= 710:
                # Need a way to get final shed state. We don't have state object here, 
                # but we can do it in track_plants instead or the caller.
                pass
            os.makedirs("experiments/metrics", exist_ok=True)
            
            def convert_defaultdicts(obj):
                if isinstance(obj, collections.defaultdict):
                    return {k: convert_defaultdicts(v) for k, v in obj.items()}
                elif isinstance(obj, dict):
                    return {k: convert_defaultdicts(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_defaultdicts(x) for x in obj]
                else:
                    return obj
                    
            output = {k: convert_defaultdicts(v) for k, v in m.items() if k != "_prev_plants"}
            
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
        
        # First collect all crops to calculate clusters, and all empty tiles
        existing_crops = []
        empty_tiles = []
        
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                tile = farm_tiles[y][x]
                if isinstance(tile, dict):
                    if tile.get("kind") == "PLANT":
                        existing_crops.append((x, y, tile.get("crop")))
                        if not tile.get("watered_today", True):
                            consecutive = tile.get("consecutive_unwatered", 0)
                            turns_until = (24 - self.state.hour) if consecutive >= 1 else (48 - self.state.hour)
                            crop_name = tile.get("crop", "")
                            crop_info = CROPS.get(crop_name, {})
                            expected_rev = self.econ.expected_sell_value(crop_name, crop_info.get("max_yield", 4))
                            urgency = expected_rev / max(1, turns_until)
                            self.tasks.append(Task("WATER", 10, (x, y), {"urgency_score": urgency, "value_score": 0}))
                        if tile.get("yield_units", 0) > 0:
                            if is_ready_to_harvest(tile.get("crop", ""), tile.get("planted_day", 0), self.state.day):
                                crop_name = tile.get("crop", "")
                                crop_info = CROPS.get(crop_name, {})
                                value = self.econ.expected_sell_value(crop_name, tile.get("yield_units", 0))
                                urgency = 0
                                if not crop_info.get("ongoing", False):
                                    deadline_step = (tile.get("planted_day", 0) + crop_info.get("max_yield_day", 0) + 1) * 24
                                    turns_until = deadline_step - self.state.step
                                    price = self.econ.expected_sell_value(crop_name, 1)
                                    if turns_until <= 0:
                                        urgency = price / 2.0
                                    else:
                                        urgency = price / max(1, turns_until)
                                self.tasks.append(Task("HARVEST", 20, (x, y), {"urgency_score": urgency, "value_score": value}))
                    elif tile.get("kind") in ["COOP", "PASTURE"]:
                        if not tile.get("fed_today", True):
                            if simulated_shed.get("WHEAT", 0) > 0:
                                consecutive = tile.get("consecutive_unfed", 0)
                                turns_until = (24 - self.state.hour) if consecutive >= 1 else (48 - self.state.hour)
                                animal_name = tile.get("animal", "")
                                animal_info = ANIMALS.get(animal_name, {})
                                expected_loss = animal_info.get("cost", 300) + 100
                                urgency = expected_loss / max(1, turns_until)
                                self.tasks.append(Task("FEED", 10, (x, y), {"urgency_score": urgency, "value_score": 0}))
                                simulated_shed["WHEAT"] -= 1
                elif tile is None:
                    empty_tiles.append((x, y))
                    
        # Plant target crops based on spatial fragmentation scores
        total_seeds_to_plant = sum(simulated_seeds.values())
        
        # Farmer's position serves as a reference for worker travel penalty if no crops exist yet
        fx, fy = self.state.farmer
        
        while total_seeds_to_plant > 0 and empty_tiles:
            # Pick a seed to plant
            seed_to_plant = None
            for available_crop, amount in simulated_seeds.items():
                if amount > 0:
                    seed_to_plant = available_crop
                    break
                    
            if not seed_to_plant:
                break
                
            best_tile = None
            best_cost = 999999
            
            CROP_TASKS = {"WHEAT": 4, "CARROT": 5, "TOMATO": 6, "STRAWBERRY": 7, "MELON": 5}
            CROP_VALUES = {"WHEAT": 3, "CARROT": 6, "TOMATO": 10, "STRAWBERRY": 25, "MELON": 40}
            
            # Estimate labor capacity and target clusters
            active_workers = len(self.state.my_farm.get("hands", [])) + 1
            current_tasks_count = len(self.tasks)
            labor_capacity = (active_workers * 24) - current_tasks_count
            target_cluster_count = max(1, labor_capacity // 30)
            
            # Simple cluster count estimation (distance <= 2)
            current_cluster_count = 0
            if existing_crops:
                visited = set()
                for p in existing_crops:
                    loc = (p[0], p[1])
                    if loc not in visited:
                        current_cluster_count += 1
                        q = [loc]
                        while q:
                            curr = q.pop(0)
                            if curr not in visited:
                                visited.add(curr)
                                for other in existing_crops:
                                    oloc = (other[0], other[1])
                                    if oloc not in visited and abs(curr[0] - oloc[0]) + abs(curr[1] - oloc[1]) <= 2:
                                        q.append(oloc)
            
            for ex, ey in empty_tiles:
                # Calculate cost for this empty tile
                worker_travel_penalty = abs(fx - ex) + abs(fy - ey)
                
                if existing_crops:
                    min_dist_to_crop = min(abs(cx - ex) + abs(cy - ey) for cx, cy, _ in existing_crops)
                    
                    # cluster_density_bonus: count adjacent crops
                    adjacent_crops = sum(1 for cx, cy, _ in existing_crops if abs(cx - ex) + abs(cy - ey) == 1)
                    cluster_density_bonus = -1 * adjacent_crops
                    
                    # future_task_density_penalty: count future tasks within distance 3
                    local_future_tasks = 0
                    for cx, cy, ccrop in existing_crops:
                        if abs(cx - ex) + abs(cy - ey) <= 3:
                            local_future_tasks += CROP_TASKS.get(ccrop, 5)
                            
                    future_task_density_penalty = 10 if local_future_tasks > 30 else 0
                    economic_value_bonus = CROP_VALUES.get(seed_to_plant, 5) * 0.1
                    
                    if min_dist_to_crop > 2 and current_cluster_count < target_cluster_count:
                        isolated_tile_penalty = 0
                    else:
                        isolated_tile_penalty = 10 if min_dist_to_crop > 1 else 0
                    
                    cost = min_dist_to_crop + cluster_density_bonus + future_task_density_penalty - economic_value_bonus + isolated_tile_penalty + (worker_travel_penalty * 0.1)
                else:
                    # If no crops exist, just cluster near the farmer to start the patch
                    cost = worker_travel_penalty
                    
                if cost < best_cost:
                    best_cost = cost
                    best_tile = (ex, ey)
                    best_cost_min_dist = min_dist_to_crop if existing_crops else 999
                    
            if best_tile:
                crop_info = CROPS.get(seed_to_plant, {})
                seed_cost = crop_info.get("seed", 0)
                expected_rev = self.econ.expected_sell_value(seed_to_plant, crop_info.get("max_yield", 4))
                remaining_days = 30 - self.state.day
                value = expected_rev - seed_cost
                if remaining_days - 1 < crop_info.get("first_yield_day", 999):
                    value = 0
                self.tasks.append(Task("PLANT", 30, best_tile, {"crop": seed_to_plant, "urgency_score": 0, "value_score": value}))
                simulated_seeds[seed_to_plant] -= 1
                total_seeds_to_plant -= 1
                empty_tiles.remove(best_tile)
                existing_crops.append((best_tile[0], best_tile[1], seed_to_plant))
                if best_cost_min_dist > 2:
                    current_cluster_count += 1
            else:
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
            
            # V009-B: Dynamically cap max yield based on remaining days in season (30 days total)
            remaining_days = 30 - self.state.day
            crop_info = CROPS.get(crop_name, {})
            first_yield = crop_info.get("first_yield_day", 999)
            
            if remaining_days - 1 < first_yield:
                achievable_yield = 0
            else:
                if crop_info.get("ongoing"):
                    possible_productions = (remaining_days - 1 - first_yield) // 2 + 1
                    actual_productions = min(crop_info["max_yield"], max(0, possible_productions))
                    multiplier = actual_productions / float(crop_info["max_yield"])
                    achievable_yield = int(crop_max_yield[crop_name] * multiplier)
                else:
                    window_start = (crop_info["max_yield_day"] + 1) // 2
                    bonus_days = max(0, min(crop_info["max_yield_day"], remaining_days - 1) - window_start + 1)
                    # Assume fertilized bonus if we have money/fertilizer policy, but for conservative estimate let's use +1 (unfertilized) or +2 (fertilized)
                    # The agent doesn't use fertilizer currently, so +1
                    base = 1
                    actual_yield_count = min(crop_info["max_yield"], base + bonus_days * 1)
                    # Scale according to crop_max_yield table which assumed max_yield (4 for wheat, but wait crop_max_yield has 6 for wheat which is fertilized)
                    multiplier = actual_yield_count / float(crop_info["max_yield"])
                    achievable_yield = int(crop_max_yield[crop_name] * multiplier)
            
            # Count pipeline (shed + planted)
            planted_count = sum(1 for y in range(self.state.board_size) for x in range(self.state.board_size) 
                              if isinstance(farm_tiles[y][x], dict) and farm_tiles[y][x].get("kind") == "PLANT" and farm_tiles[y][x].get("crop") == crop_name)
            
            pipeline_qty = self.state.shed.get(crop_name, 0) + (planted_count + self.state.seeds.get(crop_name, 0)) * crop_max_yield[crop_name]
            
            # 1. Expected Revenue (of the new crop)
            current_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
            sim_inv = current_inv + pipeline_qty
            expected_revenue = 0
            for i in range(achievable_yield):
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
        if self.state.seeds.get(target_crop, 0) == 0 and self.state.money > self.strategy.config.cash_reserve + CROPS[target_crop]["seed"]:
            if best_profit_per_action > 0:
                buy_qty = min(self.state.money // CROPS[target_crop]["seed"], 5)
                self.tasks.append(Task("BUY_SEED", 50, kwargs={"product": target_crop, "quantity": buy_qty}))
        
        # Land Expansion Logic (V010-B)
        # 1. Count number of empty unlocked tiles
        # 2. If <= 5 empty tiles left, we are capacity constrained. Buy land!
        if len(empty_tiles) <= 5:
            unlocked_quads = self.state.my_farm.get("unlocked_quadrants", [])
            n_unlocked = len(unlocked_quads)
            
            land_prices = [1000, 2000, 4000]
            
            # Note: "NW" is given for free, so n_unlocked is 1 initially.
            # We can unlock up to 3 extra quadrants: NE, SW, SE
            if n_unlocked >= 1 and n_unlocked <= 3:
                next_cost = land_prices[n_unlocked - 1]
                # Only buy if we have plenty of cash left over for seeds/labor
                if self.state.money > next_cost + self.strategy.config.cash_reserve + 2000:
                    self.tasks.append(Task("BUY_LAND", priority=100))
        
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
            if t.action_type in ["SELL", "BUY_SEED", "HIRE", "BUY_LAND"]:
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
                elif t.action_type == "HIRE":
                    market_actions.append(["HIRE"])
                    cost = self.econ.get_hire_cost(self.state.hires_today)
                    self.metrics["workers"]["hired"] += 1
                    self.metrics["workers"]["cost"] += cost
                    self.metrics["economy"]["worker_spending"] += cost
                    self.metrics["economy"]["total_spending"] += cost
                elif t.action_type == "BUY_LAND":
                    market_actions.append(["BUY_LAND"])
                    
                    unlocked_quads = self.state.my_farm.get("unlocked_quadrants", [])
                    n_unlocked = len(unlocked_quads)
                    if n_unlocked >= 1 and n_unlocked <= 3:
                        cost = [1000, 2000, 4000][n_unlocked - 1]
                        self.metrics["economy"]["total_spending"] += cost
                        if "land_spending" not in self.metrics["economy"]:
                            self.metrics["economy"]["land_spending"] = 0
                        self.metrics["economy"]["land_spending"] += cost
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
                        v_score = target.kwargs.get("value_score", 0)
                        # Soft optimization: minimize distance, maximize priority + value
                        cost = (dist * 10) - target.priority - v_score

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
        
        MetricsTracker.save(state.player, state.step, state.money, state.private.get("shed", {}), actions=actions, day=state.day)
        return actions
        
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
