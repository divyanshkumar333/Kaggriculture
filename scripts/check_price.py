import sys, types

CROPS = {
    'WHEAT': {'seed': 10, 'first_yield_day': 2, 'max_yield_day': 4, 'max_yield': 4, 'ongoing': False},
}
kenv = types.ModuleType('kaggle_environments')
kenv.envs = types.ModuleType('kaggle_environments.envs')
kenv.envs.kaggriculture = types.ModuleType('kaggle_environments.envs.kaggriculture')
kenv.envs.kaggriculture.kaggriculture = types.SimpleNamespace(CROPS=CROPS)
for k, v in [
    ('kaggle_environments', kenv),
    ('kaggle_environments.envs', kenv.envs),
    ('kaggle_environments.envs.kaggriculture', kenv.envs.kaggriculture),
    ('kaggle_environments.envs.kaggriculture.kaggriculture', kenv.envs.kaggriculture.kaggriculture),
]:
    sys.modules[k] = v

scipy_mod = types.ModuleType('scipy')
scipy_opt = types.ModuleType('scipy.optimize')
scipy_opt.linear_sum_assignment = lambda c: (list(range(c.shape[0])), list(range(c.shape[1])))
scipy_mod.optimize = scipy_opt
sys.modules['scipy'] = scipy_mod
sys.modules['scipy.optimize'] = scipy_opt

import importlib.util, os
spec = importlib.util.spec_from_file_location('v018_f', 'agents/v018_f_subsistence_fixed.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

state = types.SimpleNamespace(
    day=5, step=120, hour=0, player=0, board_size=10, money=10000,
    farmer=(5, 5), hands=[], seeds={}, shed={},
    market={'inventory': {'WHEAT': 100000}, 'prices': {}},
    my_farm={
        'tiles': [[None]*10 for _ in range(10)],
        'farmer': [5, 5], 'hands': [], 'unlocked_quadrants': ['NW'], 'hires_today': 0,
    },
    hires_today=0,
)
econ = mod.EconomicCalculator(state)

p1 = econ.get_price_at_inventory('WHEAT', 100000)
print(f'Price at inv=100000: {p1}')
p2 = econ.get_price_at_inventory('WHEAT', 200000)
print(f'Price at inv=200000: {p2}')
revenue = sum(econ.get_price_at_inventory('WHEAT', 100000 + i) for i in range(6))
print(f'Total revenue for 6 wheat at inv=100000: {revenue}')
print(f'Seed cost: 10')
print(f'Net (sunk_labor): {revenue - 10}')
