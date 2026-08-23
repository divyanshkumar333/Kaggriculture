from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
import math
import os
import json
import collections

# ==========================================
# Metrics Tracking (Phase 3)
# ==========================================
# We use a global dict keyed by the seed (passed from experiments.py)
# so the data persists across the 720 steps.
_METRICS = collections.defaultdict(lambda: {
    "workers": {"hired": 0, "cost": 0, "active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0},
    "farmer": {"active_turns": 0, "idle_turns": 0, "movement_actions": 0, "useful_actions": 0},
    "economy": {"total_spending": 0, "total_revenue": 0, "seed_spending": 0, "worker_spending": 0},
    "crops": collections.defaultdict(lambda: {"planted": 0, "watered": 0, "harvested": 0}),
    "market": collections.defaultdict(lambda: {"sold": 0, "revenue": 0})
})

class MetricsTracker:
    @staticmethod
    def get():
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        return _METRICS[seed]
    
    @staticmethod
    def save(player, step, final_money):
        seed = os.environ.get("KAGGRICULTURE_SEED", "unknown")
        m = _METRICS[seed]
        m["economy"]["final_money"] = final_money
        
        # Calculate efficiencies
        total_worker_turns = m["workers"]["active_turns"] + m["workers"]["idle_turns"]
        m["efficiency"] = {
            "worker_utilization_pct": m["workers"]["active_turns"] / max(1, total_worker_turns) * 100,
            "farmer_utilization_pct": m["farmer"]["active_turns"] / max(1, m["farmer"]["active_turns"] + m["farmer"]["idle_turns"]) * 100,
            "useful_actions_total": m["farmer"]["useful_actions"] + m["workers"]["useful_actions"]
        }
        
        # Save periodically to ensure metrics are not lost
        if step % 20 == 0 or step >= 710:
            os.makedirs("experiments/metrics", exist_ok=True)
            output = {k: dict(v) if isinstance(v, collections.defaultdict) else v for k, v in m.items()}
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
        if func_name == "linear":
            return x
        elif func_name == "sq":
            return x * x
        elif func_name == "sqrt":
            return math.sqrt(x)
        elif func_name == "log":
            return math.log(1 + x)
        elif func_name == "log10":
            return math.log10(1 + x)
        elif func_name == "hinge":
            u = x / T
            return u + 8 * max(0, u - 1)**2
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
        return max(1, round(price))

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
class StrategicPlanner:
    def __init__(self, state: GameState, econ: EconomicCalculator):
        self.state = state
        self.econ = econ
        self.mode = "BALANCED" 
        self.reserve = 50 

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
                        if not tile.get("fed_today", True):
                            self.tasks.append(Task("FEED", 10, (x, y)))
                elif tile is None:
                    if self.state.seeds.get("MELON", 0) > 0:
                        self.tasks.append(Task("PLANT", 30, (x, y), {"crop": "MELON"}))
        
        for product, qty in self.state.shed.items():
            if qty > 0:
                # We want to sell up to maximum we can without hitting price floor
                # The market accepts max 10 orders per turn overall, so we shouldn't submit small orders
                # Let's find how many we can sell before marginal price drops to 1
                current_inv = self.state.market.get("inventory", {}).get(product, 10000)
                sell_qty = 0
                for i in range(qty):
                    p = self.econ.get_price_at_inventory(product, current_inv + i)
                    if p > 1:
                        sell_qty += 1
                    else:
                        break
                
                # If we can sell some for > $1, queue it. Limit to 10 per order to not over-saturate a single turn
                if sell_qty > 0:
                    sell_qty = min(sell_qty, 10)
                    self.tasks.append(Task("SELL", 5, kwargs={"product": product, "quantity": sell_qty}))
                    
        if self.state.seeds.get("MELON", 0) == 0 and self.state.money > self.strategy.reserve + CROPS["MELON"]["seed"]:
            buy_qty = min(self.state.money // CROPS["MELON"]["seed"], 5)
            self.tasks.append(Task("BUY_SEED", 50, kwargs={"product": "MELON", "quantity": buy_qty}))
        
        self.tasks.sort(key=lambda t: t.priority)
        return self.tasks

# ==========================================
# 6. Task Allocator
# ==========================================
class TaskAllocator:
    def __init__(self, state: GameState, econ: EconomicCalculator, tasks):
        self.state = state
        self.econ = econ
        self.tasks = tasks
    
    def allocate(self):
        unassigned_field_tasks = [t for t in self.tasks if t.location is not None]
        active_workers = 1 + len(self.state.hands)
        
        cost_of_next_hire = self.econ.get_hire_cost(self.state.hires_today)
        expected_roi = self.econ.marginal_roi_of_worker()
        
        if len(unassigned_field_tasks) > active_workers and expected_roi > cost_of_next_hire:
            if self.state.money > cost_of_next_hire + 50:
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
            if t.action_type in ["SELL", "BUY_SEED", "HIRE"]:
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
            elif t.location is not None:
                field_tasks.append(t)
                
        units = [self.state.farmer] + self.state.hands
        unit_actions = []
        
        for ui, (ux, uy) in enumerate(units):
            action = ["PASS"]
            if field_tasks:
                field_tasks.sort(key=lambda t: (t.priority, abs(t.location[0] - ux) + abs(t.location[1] - uy)))
                target = field_tasks[0]
                tx, ty = target.location
                
                if ux == tx and uy == ty:
                    if target.action_type == "PLANT":
                        action = ["PLANT", target.kwargs["crop"]]
                        self.metrics["crops"][target.kwargs["crop"]]["planted"] += 1
                    else:
                        action = [target.action_type]
                        if target.action_type == "WATER":
                            # Hacky tracking of watered crops (assuming target plant hasn't vanished)
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                self.metrics["crops"][tile["crop"]]["watered"] += 1
                        elif target.action_type == "HARVEST":
                            tile = self.state.get_tile(tx, ty)
                            if tile and tile.get("kind") == "PLANT":
                                self.metrics["crops"][tile["crop"]]["harvested"] += 1
                else:
                    action = [self.step_toward(ux, uy, tx, ty)]
                field_tasks.pop(0)
                
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
        if not state.my_farm:
            return {"farmer": ["PASS"], "hands": [], "market": []}
            
        econ = EconomicCalculator(state)
        strategy = StrategicPlanner(state, econ)
        planner = DailyPlanner(state, econ, strategy)
        
        tasks = planner.plan_tasks()
        
        allocator = TaskAllocator(state, econ, tasks)
        assignments = allocator.allocate()
        
        executor = ActionExecutor(state, econ)
        actions = executor.execute(tasks, assignments)
        
        MetricsTracker.save(state.player, state.step, state.money)
        return actions
        
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"farmer": ["PASS"], "hands": [], "market": []}
