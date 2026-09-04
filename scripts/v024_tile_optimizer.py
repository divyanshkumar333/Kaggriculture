"""
Tile-Level Economic Model & Succession Optimizer (Phase 4 & 5)
==============================================================

Calculates the net expected remaining contribution to final Day-30 bank
for every crop choice on every tile, given current in-game day, crop age,
remaining season days, market prices, seed costs, and labor requirements.
"""

import math

CROP_PROPERTIES = {
    "WHEAT": {
        "seed_cost": 10,
        "first_yield_day": 2,
        "max_yield_day": 4,
        "base_yield": 1,
        "bonus_yield_per_day": 1,
        "base_price": 60,
        "is_ongoing": False,
        "requires_feed": False,
    },
    "CARROT": {
        "seed_cost": 20,
        "first_yield_day": 2,
        "max_yield_day": 4,
        "base_yield": 1,
        "bonus_yield_per_day": 1,
        "base_price": 75,
        "is_ongoing": False,
        "requires_feed": False,
    },
    "STRAWBERRY": {
        "seed_cost": 20,
        "first_yield_day": 4,
        "max_yield_day": 16,
        "base_yield": 1, # every 2 days
        "base_price": 100,
        "is_ongoing": True,
        "max_lifetime_days": 16, # cumulative production cap
    },
    "MELON": {
        "seed_cost": 80,
        "first_yield_day": 10,
        "max_yield_day": 14,
        "base_yield": 1,
        "bonus_yield_per_day": 1,
        "base_price": 350,
        "is_ongoing": False,
    }
}

def calculate_tile_expected_value(tile_state, current_day, market_prices=None):
    """
    Given the current state of a tile and day, compute:
    1. Expected remaining value of current state.
    2. Expected value of transitioning to each alternative crop (WHEAT, CARROT, STRAWBERRY, MELON).
    3. Optimal policy decision: KEEP, WATER, HARVEST, DIG_AND_REPLACE(crop).
    """
    if market_prices is None:
        market_prices = {"WHEAT": 50, "CARROT": 60, "STRAWBERRY": 75, "MELON": 250}
        
    days_left = 30 - current_day
    
    # Evaluate prospective new plantings on an empty/cleared tile
    new_crop_values = {}
    
    # 1. Prospective WHEAT planting
    if current_day <= 27:
        maturation_days = 2
        cycles = max(0, (days_left - 1) // maturation_days)
        # In practice, with fast 2-day harvesting, 1 planting on day 21 yields at d=23, d=25, d=27, d=29 (up to cycles)
        # Yield per harvest ~1-2 units (price ~$45-$55)
        unit_price = market_prices.get("WHEAT", 50)
        # Expected yield: 2 units per 2-day cycle if watered
        exp_revenue = cycles * 2 * unit_price
        seed_cost = CROP_PROPERTIES["WHEAT"]["seed_cost"]
        watering_labor = cycles * 2 * 2 # labor opportunity value ~$2/turn
        net_wheat_val = exp_revenue - seed_cost - watering_labor
        new_crop_values["WHEAT"] = max(0, net_wheat_val)
    else:
        new_crop_values["WHEAT"] = -10 # Cannot mature before day 30
        
    # 2. Prospective CARROT planting
    if current_day <= 27:
        maturation_days = 2
        cycles = max(0, (days_left - 1) // maturation_days)
        unit_price = market_prices.get("CARROT", 60)
        exp_revenue = cycles * 2 * unit_price
        seed_cost = CROP_PROPERTIES["CARROT"]["seed_cost"]
        watering_labor = cycles * 2 * 2
        new_crop_values["CARROT"] = max(0, exp_revenue - seed_cost - watering_labor)
    else:
        new_crop_values["CARROT"] = -20
        
    # 3. Prospective STRAWBERRY planting
    if current_day <= 20: # Needs 4 days to first yield
        active_production_days = max(0, days_left - 4)
        harvests = active_production_days // 1 # watered daily -> yield daily/every 2 days
        unit_price = market_prices.get("STRAWBERRY", 75)
        exp_revenue = harvests * 1.5 * unit_price
        seed_cost = CROP_PROPERTIES["STRAWBERRY"]["seed_cost"]
        new_crop_values["STRAWBERRY"] = max(0, exp_revenue - seed_cost - (active_production_days * 3))
    else:
        new_crop_values["STRAWBERRY"] = -20 # Too late to recoup strawberry investment
        
    # 4. Prospective MELON planting
    if current_day <= 16: # Needs 10 days to mature + watering bonus
        unit_price = market_prices.get("MELON", 250)
        exp_revenue = 4 * unit_price # 4 melons if watered in window
        seed_cost = CROP_PROPERTIES["MELON"]["seed_cost"]
        new_crop_values["MELON"] = max(0, exp_revenue - seed_cost - 30)
    else:
        new_crop_values["MELON"] = -80
        
    best_new_crop = max(new_crop_values.items(), key=lambda x: x[1])
    
    # Evaluate current tile state
    if tile_state is None:
        # Empty tile
        return {
            "current_value": 0,
            "best_action": f"PLANT_{best_new_crop[0]}" if best_new_crop[1] > 0 else "PASS",
            "best_crop": best_new_crop[0],
            "expected_gain": best_new_crop[1]
        }
        
    kind = tile_state.get("kind")
    if kind == "WEED":
        return {
            "current_value": 0,
            "best_action": "DIG",
            "best_crop": best_new_crop[0],
            "expected_gain": best_new_crop[1] - 5 # Dig transition cost
        }
        
    if kind == "PLANT":
        crop = tile_state.get("crop")
        planted_day = tile_state.get("planted_day", current_day)
        age = current_day - planted_day
        yield_units = tile_state.get("yield_units", 0)
        
        if crop == "STRAWBERRY":
            # Strawberry lifetime production cap ~14-16 days
            # If age >= 12, remaining days of yield are small (<= 2-4 days)
            remaining_yield_days = max(0, min(days_left, 16 - age))
            unit_price = market_prices.get("STRAWBERRY", 75)
            
            # Remaining value if kept
            if remaining_yield_days <= 1:
                # Virtually dead / decaying
                rem_val = yield_units * unit_price
            else:
                rem_val = (yield_units + remaining_yield_days * 1.0) * unit_price - (remaining_yield_days * 2)
                
            # Replacement value (DIG + Plant best new crop)
            transition_cost = 5 # 1 turn to DIG
            replacement_val = best_new_crop[1] - transition_cost
            
            if replacement_val > rem_val + 20 and current_day <= 27:
                return {
                    "current_value": rem_val,
                    "best_action": "DIG_AND_REPLACE",
                    "best_crop": best_new_crop[0],
                    "expected_gain": replacement_val - rem_val,
                    "age": age,
                    "rem_yield_days": remaining_yield_days
                }
            else:
                return {
                    "current_value": rem_val,
                    "best_action": "HARVEST" if yield_units > 0 else "WATER",
                    "best_crop": "STRAWBERRY",
                    "expected_gain": 0,
                    "age": age,
                    "rem_yield_days": remaining_yield_days
                }
                
        elif crop == "WHEAT":
            unit_price = market_prices.get("WHEAT", 50)
            if age >= 2 and yield_units > 0:
                return {"current_value": yield_units * unit_price, "best_action": "HARVEST", "best_crop": "WHEAT", "expected_gain": 0}
            else:
                return {"current_value": 2 * unit_price, "best_action": "WATER", "best_crop": "WHEAT", "expected_gain": 0}
                
    return {"current_value": 0, "best_action": "PASS", "best_crop": None, "expected_gain": 0}

if __name__ == "__main__":
    print("=== TILE ECONOMIC OPTIMIZER SIMULATION ===")
    for day in [15, 18, 20, 22, 24, 26, 27, 28, 29]:
        print(f"\n--- DAY {day} (Days Left: {30-day}) ---")
        
        # Test Empty Tile
        res_empty = calculate_tile_expected_value(None, day)
        print(f"Empty Tile: Action={res_empty['best_action']}, Best Crop={res_empty['best_crop']}, Exp Value=${res_empty['expected_gain']:.1f}")
        
        # Test Strawberry Bush planted on Day 10 (Age = day - 10)
        res_straw = calculate_tile_expected_value({"kind": "PLANT", "crop": "STRAWBERRY", "planted_day": 10, "yield_units": 0}, day)
        print(f"Strawberry (Planted D10, Age {day-10}): Action={res_straw['best_action']}, Rem Value=${res_straw['current_value']:.1f}, Action Gain=${res_straw['expected_gain']:.1f}")
