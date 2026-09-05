import pathlib

# Read V027
v27_code = pathlib.Path('agents/v027_hierarchical_meta.py').read_text(encoding='utf-8')
v27_base = v27_code.replace('def agent(obs):', 'def v027_agent(obs):')

# ==============================================================================
# V028 Market B (Impact Ordering)
# ==============================================================================
middleware_b = '''
import math

_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}

_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25

def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq": return value * value
    if name == "sqrt": return math.sqrt(value)
    if name == "log": return math.log1p(value)
    if name == "log10": return math.log10(1.0 + value)
    raise ValueError(name)

def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))

def _is_sell(order):
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in _MARKET_PARAMS

def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (ValueError, TypeError):
        quantity = 0
        
    market = getattr(obs, "market", None)
    if market is None and isinstance(obs, dict):
        market = obs.get("market", {})
        
    inventory = getattr(market, "inventory", {}) if hasattr(market, "inventory") else (market.get("inventory", {}) if isinstance(market, dict) else {})
    prices = getattr(market, "prices", {}) if hasattr(market, "prices") else (market.get("prices", {}) if isinstance(market, dict) else {})
    
    current_inventory = int(inventory.get(item, 10000)) if hasattr(inventory, "get") else 10000
    
    if hasattr(prices, "get") and item in prices:
        current_quote = float(prices[item])
    else:
        current_quote = float(_market_price(item, current_inventory))
        
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _demand_per_day(obs, configuration, item):
    town = getattr(obs, "town", {}) if hasattr(obs, "town") else (obs.get("town", {}) if isinstance(obs, dict) else {})
    shops = getattr(town, "unlocked_shops", []) if hasattr(town, "unlocked_shops") else (town.get("unlocked_shops", []) if isinstance(town, dict) else [])
    
    turns_per_day = 24
    if configuration:
        turns_per_day = int(getattr(configuration, "turnsPerDay", 24) if hasattr(configuration, "turnsPerDay") else configuration.get("turnsPerDay", 24))
        
    shop_interval = 4
    if configuration:
        shop_interval = max(1, int(getattr(configuration, "townShopSellInterval", 4) if hasattr(configuration, "townShopSellInterval") else configuration.get("townShopSellInterval", 4)))
        
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
            
    if item != "FERTILIZER":
        center_interval = 24
        if configuration:
            center_interval = max(1, int(getattr(configuration, "townCenterSellInterval", 24) if hasattr(configuration, "townCenterSellInterval") else configuration.get("townCenterSellInterval", 24)))
            
        demand += (turns_per_day / center_interval) * 1
    return demand

def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item = str(order[1])
    quantity = max(0, int(order[2]))
    
    market = getattr(obs, "market", None)
    if market is None and isinstance(obs, dict):
        market = obs.get("market", {})
        
    inventory = getattr(market, "inventory", {}) if hasattr(market, "inventory") else (market.get("inventory", {}) if isinstance(market, dict) else {})
    current_inventory = int(inventory.get(item, 10000)) if hasattr(inventory, "get") else 10000
    
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)

def _rank_sell_slots(obs, action, configuration):
    try:
        market = list(action.get("market", []))
        rows = []
        for index, order in enumerate(market):
            if _is_sell(order):
                score = _order_score(obs, configuration, order)
                rows.append((score, -index, list(order)))
                
        if len(rows) < 2:
            return action
            
        rows.sort(reverse=True)
        ranked = iter(row[2] for row in rows)
        action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
        return action
    except Exception as e:
        raise RuntimeError(f"MARKET IMPACT ORDERING CRASH: {str(e)}") from e

def _to_dict(obs):
    if isinstance(obs, dict):
        return obs
    return {
        "player": obs.player,
        "step": obs.step,
        "day": obs.day,
        "hour": obs.hour,
        "farms": [
            {
                "money": f.money,
                "tiles": f.tiles,
                "farmer": f.farmer,
                "hands": f.hands,
                "unlocked_quadrants": f.unlocked_quadrants,
                "hires_today": f.hires_today
            } for f in obs.farms
        ],
        "private": {
            "shed": obs.private.shed,
            "seeds": obs.private.seeds,
            "inventories": obs.private.inventories
        },
        "market": {
            "inventory": getattr(obs.market, "inventory", {}),
            "prices": getattr(obs.market, "prices", {})
        },
        "town": {
            "unlocked_shops": getattr(obs.town, "unlocked_shops", [])
        }
    }

def agent(obs, configuration=None):
    if configuration is None:
        configuration = {"turnsPerDay": 24, "townShopSellInterval": 4, "townCenterSellInterval": 24}
        
    try:
        obs_dict = _to_dict(obs)
        action = v027_agent(obs_dict)
        action = _rank_sell_slots(obs_dict, action, configuration)
        return action
    except Exception as e:
        raise RuntimeError(f"V028-MARKET-B CRASHED: {str(e)}") from e
'''

pathlib.Path('agents/v028_market_b.py').write_text(v27_base + '\n' + middleware_b, encoding='utf-8')

# ==============================================================================
# V028 Market A (Premium Market Lead)
# ==============================================================================
middleware_a = '''
_PREMIUM_GOODS = {"MELON", "MILK", "STRAWBERRY", "WOOL"}

def _premium_market_lead(obs, action, configuration):
    try:
        market = list(action.get("market", []))
        
        # 1. Check if town demand is 0 for premium goods this turn
        obs_dict = _to_dict(obs)
        
        # 2. To apply Premium Market Lead strictly as defined:
        # "When the current turn has no matching town demand, increase the SELL quantity 
        # to exactly match the available inventory in the shed, overriding the batch size limit."
        # This forces the sale of *all* available premium stock before the price crashes 
        # on the next turn, rather than drip-feeding it in batches.
        
        new_market = []
        for order in market:
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = order[1]
                if item in _PREMIUM_GOODS:
                    demand = _demand_per_day(obs_dict, configuration, item)
                    # If town demand is 0, unleash the full shed
                    if demand == 0:
                        shed = obs_dict.get("private", {}).get("shed", {})
                        total_stock = shed.get(item, 0)
                        if total_stock > 0:
                            order = ["SELL", item, total_stock]
            new_market.append(order)
            
        action["market"] = new_market
        return action
    except Exception as e:
        raise RuntimeError(f"PREMIUM MARKET LEAD CRASH: {str(e)}") from e

def agent(obs, configuration=None):
    if configuration is None:
        configuration = {"turnsPerDay": 24, "townShopSellInterval": 4, "townCenterSellInterval": 24}
        
    try:
        obs_dict = _to_dict(obs)
        action = v027_agent(obs_dict)
        action = _premium_market_lead(obs_dict, action, configuration)
        return action
    except Exception as e:
        raise RuntimeError(f"V028-MARKET-A CRASHED: {str(e)}") from e
'''

b_logic = middleware_b.split("def agent(obs")[0]
a_logic = middleware_a

c_agent = '''
def agent(obs, configuration=None):
    if configuration is None:
        configuration = {"turnsPerDay": 24, "townShopSellInterval": 4, "townCenterSellInterval": 24}
        
    try:
        obs_dict = _to_dict(obs)
        action = v027_agent(obs_dict)
        action = _premium_market_lead(obs_dict, action, configuration)
        action = _rank_sell_slots(obs_dict, action, configuration)
        return action
    except Exception as e:
        raise RuntimeError(f"V028-MARKET-C CRASHED: {str(e)}") from e
'''

pathlib.Path('agents/v028_market_a.py').write_text(v27_base + b_logic + a_logic.replace('demand == 0:', 'demand < 1.1: # Ignore base town center demand'), encoding='utf-8')
pathlib.Path('agents/v028_market_c.py').write_text(v27_base + b_logic + a_logic.replace('def agent(obs', 'def x_agent(obs').replace('demand == 0:', 'demand < 1.1:') + c_agent, encoding='utf-8')
