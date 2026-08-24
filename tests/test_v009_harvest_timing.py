import json
import collections

# Fake CROPS dict based on Kaggriculture rules
CROPS = {
    "WHEAT": {"first_yield_day": 2, "max_yield_day": 4, "ongoing": False, "interval": 0, "max_yield": 6, "seed": 10},
    "CARROT": {"first_yield_day": 2, "max_yield_day": 3, "ongoing": False, "interval": 0, "max_yield": 4, "seed": 20},
    "TOMATO": {"first_yield_day": 8, "max_yield_day": 11, "ongoing": True, "interval": 2, "max_yield": 4, "seed": 50},
    "STRAWBERRY": {"first_yield_day": 10, "max_yield_day": 16, "ongoing": True, "interval": 2, "max_yield": 4, "seed": 100},
    "MELON": {"first_yield_day": 10, "max_yield_day": 10, "ongoing": False, "interval": 0, "max_yield": 6, "seed": 80}
}

# The flawed V009-B logic
def v009_b_achievable_yield(crop_name, current_day):
    crop_max_yield_val = {"WHEAT": 6, "CARROT": 4, "TOMATO": 16, "STRAWBERRY": 16, "MELON": 6}[crop_name]
    remaining_days = 30 - current_day
    crop_info = CROPS.get(crop_name, {})
    first_yield = crop_info.get("first_yield_day", 999)
    
    if remaining_days < first_yield:
        achievable_multiplier = 0
    else:
        if crop_name in ["TOMATO", "STRAWBERRY"]:
            possible_productions = (remaining_days - first_yield) // 2 + 1
            actual_productions = min(4, possible_productions)
            achievable_multiplier = (actual_productions / 4.0)
        else:
            achievable_multiplier = 1.0

    return int(crop_max_yield_val * achievable_multiplier)

# The Corrected Logic
def correct_achievable_yield(crop_name, current_day, fertilized=True):
    # Maximum crop values if fully fertilized
    crop_max_yield_val = {"WHEAT": 6, "CARROT": 4, "TOMATO": 16, "STRAWBERRY": 16, "MELON": 6}[crop_name]
    remaining_days = 30 - current_day
    crop_info = CROPS.get(crop_name, {})
    first_yield = crop_info.get("first_yield_day", 999)
    
    if remaining_days - 1 < first_yield:
        return 0
        
    if crop_info["ongoing"]:
        possible_productions = (remaining_days - 1 - first_yield) // 2 + 1
        actual_productions = min(crop_info["max_yield"], max(0, possible_productions))
        multiplier = actual_productions / float(crop_info["max_yield"])
        return int(crop_max_yield_val * multiplier)
    else:
        window_start = (crop_info["max_yield_day"] + 1) // 2
        bonus_days = max(0, min(crop_info["max_yield_day"], remaining_days - 1) - window_start + 1)
        base = 1
        bonus_per_day = 2 if fertilized else 1
        actual_yield = min(crop_info["max_yield"], base + bonus_days * bonus_per_day)
        return actual_yield

def run_tests():
    test_cases = [
        ("A. Full yield one-time", "WHEAT", 0),
        ("B. Exact time for first harvest (one-time)", "WHEAT", 27),
        ("C. One day too late (one-time)", "WHEAT", 28),
        ("D. Multi-harvest (2+ harvests)", "STRAWBERRY", 16),
        ("E. Multi-harvest (Exactly 1 harvest)", "STRAWBERRY", 19),
        ("F. Multi-harvest (Too late)", "STRAWBERRY", 20),
        ("G. Day-29 planting", "CARROT", 29),
        ("H. Day-30 planting", "MELON", 30),
        ("I. Early-season planting", "TOMATO", 5),
    ]

    print(f"{'Test Case':<40} | {'Crop':<10} | {'Day':<3} | {'V009-B Yield':<15} | {'Correct Yield':<15}")
    print("-" * 95)
    for name, crop, day in test_cases:
        v009b_yield = v009_b_achievable_yield(crop, day)
        corr_yield = correct_achievable_yield(crop, day)
        print(f"{name:<40} | {crop:<10} | {day:<3} | {v009b_yield:<15} | {corr_yield:<15}")

if __name__ == '__main__':
    run_tests()
