from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS, ANIMALS
import math
import os
import json
import collections
import numpy as np
from scipy.optimize import linear_sum_assignment

# ==========================================
# Metrics Tracking (V019-B)
# ==========================================
_METRICS = collections.defaultdict(lambda: {
    "workers": {"hired": 0, "cost": 0, "active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0, "max_active": 0},
    "farmer": {"active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0},
    "economy": {"total_spending": 0, "total_revenue": 0, "seed_spending": 0, "worker_spending": 0, "final_money": 0},
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
    "v019": {
        "melon_market_prices": [],
        "alternative_crop_prices": {},
        "crop_switch_count": 0,
        "current_crop": "MELON",
        "melon_units_produced": 0,
        "alternative_units_produced": collections.defaultdict(int),
        "projected_marginal_profit": {},
        "market_saturation_events": 0,
        "end_game_unharvested_units": 0,
        "evaluations": []
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
                
            task_density = 0
            for loc, plant in current_plants.items():
                crop_name = plant.get("crop", "WHEAT")
                future_tasks = 4
                if crop_name == "MELON": future_tasks = 5
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
        
        if step % 20 == 0 or step >= 710:
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
        self.opp_player = 1 - self.player
        self.step = obs.get("step", 0)
        self.day = obs.get("day", 0)
        self.hour = obs.get("hour", 0)
        self.farms = obs.get("farms", [])
        self.my_farm = self.farms[self.player] if self.farms and len(self.farms) > self.player else {}
        self.opp_farm = self.farms[self.opp_player] if self.farms and len(self.farms) > self.opp_player else {}
        
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
        tiles = self.my_farm.get("tiles", [])
        if y < len(tiles) and x < len(tiles[y]):
            return tiles[y][x]
        return None

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

    # =========================================================================
    # Real-Time Competitive Market State & Adaptive Crop Evaluator (V019-B)
    # =========================================================================
    def evaluate_competitive_crops(self):
        """
        Evaluates every crop in the game accounting for:
        1. Current shared market inventory
        2. Our own planted pipeline + shed inventory
        3. Opponent's visible planted pipeline
        4. Achievable yield given remaining season days
        5. Lifecycle labor requirements (plant + watering + harvest)
        6. Marginal profit per action
        """
        remaining_days = 30 - self.state.day
        evaluations = {}
        
        CROP_BASE_ACTIONS = {
            "WHEAT": 6, "CARROT": 5, "TOMATO": 14, "STRAWBERRY": 16, "MELON": 12
        }
        CROP_MAX_YIELD = {
            "WHEAT": 4, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6
        }
        
        my_tiles = self.state.my_farm.get("tiles", [])
        opp_tiles = self.state.opp_farm.get("tiles", [])
        
        # Count planted crops for both players
        my_planted = collections.defaultdict(int)
        for row in my_tiles:
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    my_planted[tile.get("crop", "")] += 1
                    
        opp_planted = collections.defaultdict(int)
        for row in opp_tiles:
            for tile in row:
                if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    opp_planted[tile.get("crop", "")] += 1
                    
        unlocked_shops = self.state.town.get("unlocked_shops", [])
        
        for crop_name, crop_info in CROPS.items():
            first_yield = crop_info.get("first_yield_day", 999)
            max_yield_day = crop_info.get("max_yield_day", first_yield)
            seed_cost = crop_info.get("seed", 999)
            
            # 1. Feasibility & Achievable Yield
            if remaining_days - 1 < first_yield:
                achievable_yield = 0
            else:
                if crop_info.get("ongoing"):
                    interval = crop_info.get("interval", 1)
                    possible_yields = (remaining_days - 1 - first_yield) // max(1, interval) + 1
                    achievable_yield = min(crop_info["max_yield"], max(0, possible_yields))
                else:
                    window_start = (max_yield_day + 1) // 2
                    bonus_days = max(0, min(max_yield_day, remaining_days - 1) - window_start + 1)
                    achievable_yield = min(crop_info["max_yield"], 1 + bonus_days)
                    
            if achievable_yield <= 0:
                evaluations[crop_name] = {
                    "crop": crop_name,
                    "achievable_yield": 0,
                    "expected_revenue": 0,
                    "seed_cost": seed_cost,
                    "net_profit": -seed_cost,
                    "profit_per_action": -999999,
                    "feasible": False,
                    "projected_inventory": 10000,
                    "projected_unit_price": 1
                }
                continue
                
            # 2. Total Market Forward Pipeline
            current_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
            my_shed_qty = self.state.shed.get(crop_name, 0)
            my_pipeline_yield = my_planted[crop_name] * CROP_MAX_YIELD.get(crop_name, 4)
            opp_pipeline_yield = opp_planted[crop_name] * CROP_MAX_YIELD.get(crop_name, 4)
            
            # Approximate town consumption drain over crop growth horizon
            growth_days = max(1, min(max_yield_day, remaining_days))
            # Each shop instance drains 6/day if demanding crop
            shop_drain_rate = sum(6 for s in unlocked_shops if crop_name.lower() in s.lower()) + 1 # +1 for town center
            total_drain = growth_days * shop_drain_rate
            
            projected_inv = max(9500, current_inv + my_shed_qty + my_pipeline_yield + opp_pipeline_yield - total_drain)
            
            # 3. Projected Marginal Revenue
            expected_rev = 0
            for i in range(achievable_yield):
                p = self.get_price_at_inventory(crop_name, projected_inv + i)
                expected_rev += p
                
            projected_unit_price = self.get_price_at_inventory(crop_name, projected_inv)
            
            # 4. Action / Labor Cost
            required_actions = CROP_BASE_ACTIONS.get(crop_name, 6)
            labor_cost_per_action = 0.50
            total_labor_cost = required_actions * labor_cost_per_action
            
            # 5. Net Profit & Margin
            net_profit = expected_rev - seed_cost - total_labor_cost
            profit_per_action = net_profit / float(required_actions)
            
            evaluations[crop_name] = {
                "crop": crop_name,
                "achievable_yield": achievable_yield,
                "expected_revenue": expected_rev,
                "seed_cost": seed_cost,
                "labor_cost": total_labor_cost,
                "net_profit": net_profit,
                "profit_per_action": profit_per_action,
                "feasible": True,
                "projected_inventory": projected_inv,
                "projected_unit_price": projected_unit_price,
                "required_actions": required_actions
            }
            
        return evaluations

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
                    
        metrics = MetricsTracker.get()
        metrics["v018"]["empty_tile_days"] += len(empty_tiles)
        metrics["v018"]["productive_tile_days"] += len(existing_crops)
        
        # --- V018-B Batch Cap ---
        DAILY_PLANT_CAP = int(os.environ.get("V018_B_CAP", 4))
        
        for crop in list(simulated_seeds.keys()):
            if simulated_seeds[crop] > DAILY_PLANT_CAP:
                blocked = simulated_seeds[crop] - DAILY_PLANT_CAP
                metrics["v018"]["blocked_planting_quantity"] += blocked
                simulated_seeds[crop] = DAILY_PLANT_CAP
                
        total_seeds_to_plant = sum(simulated_seeds.values())
        fx, fy = self.state.farmer
        
        while total_seeds_to_plant > 0 and empty_tiles:
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
            
            active_workers = len(self.state.my_farm.get("hands", [])) + 1
            current_tasks_count = len(self.tasks)
            labor_capacity = (active_workers * 24) - current_tasks_count
            target_cluster_count = max(1, labor_capacity // 30)
            
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
                worker_travel_penalty = abs(fx - ex) + abs(fy - ey)
                
                if existing_crops:
                    dists = [abs(ex - cx) + abs(ey - cy) for cx, cy, _ in existing_crops]
                    min_dist_to_crop = min(dists)
                    
                    if min_dist_to_crop > 3:
                        penalty = (min_dist_to_crop - 3) * 15
                    else:
                        penalty = 0
                    
                    if current_cluster_count < target_cluster_count:
                        cluster_expansion_bonus = min_dist_to_crop * 3
                        penalty -= cluster_expansion_bonus
                        
                    near_same_crop = any(abs(ex - cx) + abs(ey - cy) <= 1 for cx, cy, ctype in existing_crops if ctype == seed_to_plant)
                    if near_same_crop:
                        penalty -= 5
                else:
                    penalty = 0
                    
                total_tile_cost = worker_travel_penalty + penalty
                if total_tile_cost < best_cost:
                    best_cost = total_tile_cost
                    best_tile = (ex, ey)
                    
            if best_tile:
                self.tasks.append(Task("PLANT", 30, best_tile, {"crop": seed_to_plant}))
                empty_tiles.remove(best_tile)
                simulated_seeds[seed_to_plant] -= 1
                total_seeds_to_plant -= 1
                existing_crops.append((best_tile[0], best_tile[1], seed_to_plant))
            else:
                break
                
        # Smart selling (holding if below floor)
        for product, qty in self.state.shed.items():
            if qty > 0:
                current_inv = self.state.market.get("inventory", {}).get(product, 10000)
                sell_qty = 0
                for i in range(qty):
                    p = self.econ.get_price_at_inventory(product, current_inv + i)
                    if p > self.strategy.config.min_sell_price:
                        sell_qty += 1
                    else:
                        break
                
                if sell_qty > 0:
                    sell_qty = min(sell_qty, self.strategy.config.sell_batch_size)
                    self.tasks.append(Task("SELL", 5, kwargs={"product": product, "quantity": sell_qty}))
                    
        # =====================================================================
        # Adaptive Market-Aware Crop Selection (V019-B)
        # =====================================================================
        evaluations = self.econ.evaluate_competitive_crops()
        
        # Track metrics
        m_v19 = metrics["v019"]
        melon_eval = evaluations.get("MELON", {})
        m_v19["melon_market_prices"].append(melon_eval.get("projected_unit_price", 1))
        
        for cname, cdata in evaluations.items():
            if cname != "MELON":
                m_v19["alternative_crop_prices"][cname] = cdata.get("projected_unit_price", 1)
                
        # Filter viable candidates
        viable_crops = [c for c, d in evaluations.items() if d["feasible"] and d["net_profit"] > 0]
        
        if viable_crops:
            # Sort by profit per action descending
            viable_crops.sort(key=lambda c: evaluations[c]["profit_per_action"], reverse=True)
            best_crop = viable_crops[0]
            best_eval = evaluations[best_crop]
            
            # Switch tracking
            prev_crop = m_v19.get("current_crop", "MELON")
            if best_crop != prev_crop:
                m_v19["crop_switch_count"] += 1
                m_v19["current_crop"] = best_crop
                if prev_crop == "MELON" and best_crop != "MELON":
                    m_v19["market_saturation_events"] += 1
        else:
            best_crop = "MELON"
            best_eval = evaluations.get("MELON", {"profit_per_action": 0})
            
        target_crop = best_crop
        
        # Purchase seeds if seed count is 0 and financially sound
        if self.state.seeds.get(target_crop, 0) == 0 and self.state.money > self.strategy.config.cash_reserve + CROPS[target_crop]["seed"]:
            if best_eval.get("profit_per_action", 0) > 0 and best_eval.get("feasible", False):
                remaining_days = 30 - self.state.day
                if remaining_days - 1 >= CROPS.get(target_crop, {}).get("first_yield_day", 999):
                    buy_qty = min(self.state.money // CROPS[target_crop]["seed"], 5)
                    self.tasks.append(Task("BUY_SEED", 50, kwargs={"product": target_crop, "quantity": buy_qty}))
        
        # Land Expansion Logic (V010-B preserved)
        if len(empty_tiles) <= 5:
            unlocked_quads = self.state.my_farm.get("unlocked_quadrants", [])
            n_unlocked = len(unlocked_quads)
            land_prices = [1000, 2000, 4000]
            if 1 <= n_unlocked <= 3:
                next_cost = land_prices[n_unlocked - 1]
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
        
        empty_unlocked = 0
        farm_tiles = self.state.my_farm.get("tiles", [])
        for y in range(self.state.board_size):
            for x in range(self.state.board_size):
                if farm_tiles[y][x] is None:
                    empty_unlocked += 1
                    
        queued_plant_tasks = sum(1 for t in unassigned_field_tasks if t.action_type == "PLANT")
        uninstantiated_plant_tasks = max(0, empty_unlocked - queued_plant_tasks)
        
        units = [self.state.farmer] + self.state.hands
        min_start_dist = 0
        if unassigned_field_tasks or uninstantiated_plant_tasks > 0:
            if unassigned_field_tasks:
                min_start_dist = min([abs(ux - tx) + abs(uy - ty) for ux, uy in units for t in unassigned_field_tasks for tx, ty in [t.location]], default=0)
            else:
                min_start_dist = min([abs(ux - 4) + abs(uy - 4) for ux, uy in units], default=0)
                
        total_tasks = len(unassigned_field_tasks) + uninstantiated_plant_tasks
        required_actions = min_start_dist + (total_tasks * 2) if total_tasks > 0 else 0
        available_worker_actions = active_workers * remaining_turns
        
        labor_deficit = required_actions - available_worker_actions
        labor_surplus = available_worker_actions - required_actions
        
        metrics["labor"]["required_sum"] += required_actions
        metrics["labor"]["available_sum"] += available_worker_actions
        metrics["labor"]["deficit_sum"] += max(0, labor_deficit)
        metrics["labor"]["surplus_sum"] += max(0, labor_surplus)
        
        cost_of_next_hire = self.econ.get_hire_cost(self.state.hires_today)
        expected_roi = self.strategy.config.worker_roi_threshold
        
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
                    self.metrics["market"][t.kwargs["product"]]["sold"] += t.kwargs["quantity"]
                    current_price = self.state.market.get("prices", {}).get(t.kwargs["product"], 1)
                    self.metrics["market"][t.kwargs["product"]]["revenue"] += current_price * t.kwargs["quantity"]
                    self.metrics["economy"]["total_revenue"] += current_price * t.kwargs["quantity"]
                    
                    crop = t.kwargs["product"]
                    revenue = current_price * t.kwargs["quantity"]
                    if crop in ["TOMATO", "STRAWBERRY", "MELON"]:
                        self.metrics["v018"]["premium_revenue"] += revenue
                    else:
                        self.metrics["v018"]["staple_revenue"] += revenue
                        
                    if crop in ["WHEAT", "CARROT"]:
                        self.metrics["v018"]["filler_revenue"] += revenue
                        
                    self.metrics["v018"]["sale_prices"].append(current_price)

                elif t.action_type == "BUY_SEED":
                    market_actions.append(["BUY_SEED", t.kwargs["product"], t.kwargs["quantity"]])
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
                    land_prices = [1000, 2000, 4000]
                    cost = land_prices[n_unlocked - 1] if 1 <= n_unlocked <= 3 else 0
                    if "land_spending" not in self.metrics["economy"]:
                        self.metrics["economy"]["land_spending"] = 0
                    self.metrics["economy"]["land_spending"] += cost
                    self.metrics["economy"]["total_spending"] += cost

            elif t.location is not None:
                field_tasks.append(t)
                
        units = [self.state.farmer] + self.state.hands
        unit_actions = []
        assigned_targets = [None] * len(units)
        
        if field_tasks:
            cost_matrix = np.zeros((len(units), len(field_tasks)))
            for i, (ux, uy) in enumerate(units):
                for j, target in enumerate(field_tasks):
                    tx, ty = target.location
                    dist = abs(ux - tx) + abs(uy - ty)
                    
                    if target.action_type == "HARVEST":
                        val = target.kwargs.get("value_score", 0)
                        urgency = target.kwargs.get("urgency_score", 0)
                        cost = (dist * 10) - (target.priority * 2) - urgency - (val * 0.05)
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
                        self.metrics["crops"][target.kwargs["crop"]]["planted"] += 1
                        
                        crop = target.kwargs["crop"]
                        metrics = MetricsTracker.get()
                        
                        if crop in ["TOMATO", "STRAWBERRY", "MELON"]:
                            metrics["v018"]["premium_crop_quantity"] += 1
                        else:
                            metrics["v018"]["staple_crop_quantity"] += 1
                            
                        market_inv = self.state.market.get("inventory", {}).get(crop, 10000)
                        price = self.econ.get_price_at_inventory(crop, market_inv)
                        metrics["v018"]["planting_prices"].append(price)
                        
                        if "batches_today" not in metrics["v018"]:
                            metrics["v018"]["batches_today"] = {}
                        if crop not in metrics["v018"]["batches_today"]:
                            metrics["v018"]["batches_today"][crop] = 0
                        metrics["v018"]["batches_today"][crop] += 1

                    else:
                        action = [target.action_type]
                        if target.action_type == "WATER":
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                self.metrics["crops"][tile["crop"]]["watered"] += 1
                        elif target.action_type == "HARVEST":
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                crop_name = tile["crop"]
                                self.metrics["crops"][crop_name]["harvested"] += 1
                                if crop_name == "MELON":
                                    metrics["v019"]["melon_units_produced"] += tile.get("yield_units", 1)
                                else:
                                    metrics["v019"]["alternative_units_produced"][crop_name] += tile.get("yield_units", 1)
                                    
                                market_inv = self.state.market.get("inventory", {}).get(crop_name, 10000)
                                price = self.econ.get_price_at_inventory(crop_name, market_inv)
                                metrics["v018"]["harvest_prices"].append(price)

                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
                    
                if "assignments_count" not in self.metrics["workers"]:
                    self.metrics["workers"]["assignments_count"] = 0
                    self.metrics["workers"]["total_assignment_distance"] = 0
                self.metrics["workers"]["assignments_count"] += 1
                self.metrics["workers"]["total_assignment_distance"] += abs(ux - tx) + abs(uy - ty)
                
            unit_actions.append(action)
            
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
        
        m = MetricsTracker.get()
        if state.hour == 23:
            if "batches_today" in m["v018"]:
                for crop, qty in m["v018"]["batches_today"].items():
                    m["v018"]["batches"].append({"crop": crop, "qty": qty})
                m["v018"]["batches_today"] = {}
                
        MetricsTracker.save(state.player, state.step, state.money, state.private.get("shed", {}), actions=actions, day=state.day)
        return actions
        
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
