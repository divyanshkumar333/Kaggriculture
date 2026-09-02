"""
Generator for V023 Candidates A, B, C, D directly from V022-C Master Source
"""

import hashlib
import importlib.util
from kaggle_environments import make

with open("agents/v022_c_market_batching.py", "r") as f:
    master_v22 = f.read()

# -----------------------------------------------------------------------------
# CANDIDATE V023-A: Fast Cow & Pasture Acceleration
# -----------------------------------------------------------------------------
# 1. Pastures target 8 on Day 6 instead of waiting for Day 10
# 2. Allows buying 2 cows/turn when money >= 3000 on Days 6+
v023_a = master_v22.replace(
    'target_pasture_count = 4 if day < 6 else (8 if day < 10 else 15)',
    'target_pasture_count = 4 if day < 6 else (8 if day < 8 else 15)'
).replace(
    '''            if day >= 6 and money >= 600 and num_animals < 15:
                if num_cows < 11 and (len(empty_structures) > 0 or shed.get("COW", 0) == 0):
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                elif num_sheep < 4 and (len(empty_structures) > 0 or shed.get("SHEEP", 0) == 0):
                    market_orders.append(["BUY_ANIMAL", "SHEEP", 1])''',
    '''            if day >= 6 and num_animals < 15:
                if num_cows < 11 and (len(empty_structures) > 0 or shed.get("COW", 0) < 2):
                    n_buy = 2 if money >= 3500 else (1 if money >= 1500 else 0)
                    for _ in range(n_buy):
                        if len(market_orders) < 8 and num_cows < 11:
                            market_orders.append(["BUY_ANIMAL", "COW", 1])
                elif num_sheep < 4 and (len(empty_structures) > 0 or shed.get("SHEEP", 0) == 0) and money >= 1000:
                    market_orders.append(["BUY_ANIMAL", "SHEEP", 1])'''
)

with open("agents/v023_a_cow_acceleration.py", "w") as f:
    f.write(v023_a)

# -----------------------------------------------------------------------------
# CANDIDATE V023-B: Strawberry Early Ramp (Days 6-10)
# -----------------------------------------------------------------------------
# V023-A + Starts planting strawberries in Quad 2 on Day 6 instead of Day 10
v023_b = v023_a.replace(
    '''            if day >= 10 and day <= 24 and money >= 300:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                if (num_strawberries + straw_seeds) < 45 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 45 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])''',
    '''            if day >= 6 and day <= 24 and money >= 300:
                straw_seeds = seeds.get("STRAWBERRY", 0)
                target_straw = 20 if day < 9 else 45
                if (num_strawberries + straw_seeds) < target_straw and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, target_straw - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])'''
).replace(
    'chosen_crop = "MELON" if avail_melon > 0 and day < 5 else ("STRAWBERRY" if avail_straw > 0 and day >= 8 else "WHEAT")',
    'chosen_crop = "MELON" if avail_melon > 0 and day < 5 else ("STRAWBERRY" if avail_straw > 0 and day >= 6 else "WHEAT")'
).replace(
    'target_hands = 6 if money >= 80 else 4',
    'target_hands = 8 if money >= 120 else 6'
)

with open("agents/v023_b_strawberry_early_ramp.py", "w") as f:
    f.write(v023_b)

# -----------------------------------------------------------------------------
# CANDIDATE V023-C: Late-Season Crop Succession (Days 22-29)
# -----------------------------------------------------------------------------
# V023-B + Replanting freed decaying strawberry tiles with Wheat & Carrots
v023_c = v023_b.replace(
    '''            if day >= 6 and day <= 26:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 10 and money >= 100:
                    market_orders.append(["BUY_SEED", "WHEAT", 4])''',
    '''            if day >= 22 and day <= 26 and money >= 200:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 30 and len(empty_unlocked_tiles) > 2:
                    market_orders.append(["BUY_SEED", "WHEAT", min(10, 30 - (num_wheat_plants + wheat_seeds))])
            elif day >= 6 and day < 22:
                wheat_seeds = seeds.get("WHEAT", 0)
                if (num_wheat_plants + wheat_seeds) < 10 and money >= 100:
                    market_orders.append(["BUY_SEED", "WHEAT", 4])'''
)

with open("agents/v023_c_late_crop_succession.py", "w") as f:
    f.write(v023_c)

# -----------------------------------------------------------------------------
# CANDIDATE V023-D: Full Integrated Industrial Flywheel
# -----------------------------------------------------------------------------
# V023-C + Optimized dynamic task-matched labor scaling up to 13 workers
v023_d = v023_c.replace(
    '''            elif num_quads >= 4:
                target_hands = 12 if money >= 350 else 8''',
    '''            elif num_quads >= 4:
                target_hands = 13 if day >= 20 and money >= 400 else (12 if money >= 300 else 8)'''
)

with open("agents/v023_d_integrated_flywheel.py", "w") as f:
    f.write(v023_d)

print("Generated clean V023-A, B, C, D candidates.")

# Smoke verify all 4 candidates
for name, fpath in [
    ("V022-C Control", "agents/v022_c_market_batching.py"),
    ("V023-A", "agents/v023_a_cow_acceleration.py"),
    ("V023-B", "agents/v023_b_strawberry_early_ramp.py"),
    ("V023-C", "agents/v023_c_late_crop_succession.py"),
    ("V023-D", "agents/v023_d_integrated_flywheel.py")
]:
    spec = importlib.util.spec_from_file_location("ag", fpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=False)
    env.run([mod.agent, "random"])
    score = env.steps[-1][0]["reward"]
    print(f"Smoke Test {name:<10}: Score = ${score:7,.0f}")
