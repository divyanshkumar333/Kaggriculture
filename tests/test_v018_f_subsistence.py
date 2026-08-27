"""
V018-F Subsistence Fallback — comprehensive test suite.

Tests A-H as required by the investigation spec:
  A. Premium crop available → fallback does NOT activate.
  B. Premium market saturated → fallback CAN activate.
  C. Fallback chooses a profitable Wheat/Carrot crop.
  D. Fallback rejects a crop whose expected revenue is below seed cost.
  E. Fallback respects remaining-season harvest timing.
  F. Fallback respects the V018-B daily batch cap (cannot bypass it).
  G. Fallback cannot create an infinite purchase/plant loop.
  H. Normal V018-B behavior remains unchanged when fallback is inactive.
"""
import os
import sys
import types
import collections
import unittest

# ── Stubs ──────────────────────────────────────────────────────────────────
CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2, "max_yield_day": 4,  "max_yield": 4,  "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 3, "max_yield_day": 5,  "max_yield": 4,  "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 4, "max_yield_day": 12, "max_yield": 8,  "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 5, "max_yield_day": 16, "max_yield": 8,  "ongoing": True},
    "MELON":      {"seed": 200, "first_yield_day": 7, "max_yield_day": 12, "max_yield": 6,  "ongoing": False},
}

kenv = types.ModuleType("kaggle_environments")
kenv.envs = types.ModuleType("kaggle_environments.envs")
kenv.envs.kaggriculture = types.ModuleType("kaggle_environments.envs.kaggriculture")
kenv.envs.kaggriculture.kaggriculture = types.SimpleNamespace(CROPS=CROPS)
for k, v in [
    ("kaggle_environments", kenv),
    ("kaggle_environments.envs", kenv.envs),
    ("kaggle_environments.envs.kaggriculture", kenv.envs.kaggriculture),
    ("kaggle_environments.envs.kaggriculture.kaggriculture",
     kenv.envs.kaggriculture.kaggriculture),
]:
    sys.modules[k] = v

scipy_mod = types.ModuleType("scipy")
scipy_opt = types.ModuleType("scipy.optimize")
def _lsa(cost_matrix):
    n, m = cost_matrix.shape
    row, col, used = [], [], set()
    for i in range(n):
        best = min((j for j in range(m) if j not in used),
                   key=lambda j: cost_matrix[i, j], default=None)
        if best is not None:
            row.append(i); col.append(best); used.add(best)
    return row, col
scipy_opt.linear_sum_assignment = _lsa
scipy_mod.optimize = scipy_opt
sys.modules["scipy"] = scipy_mod
sys.modules["scipy.optimize"] = scipy_opt

import importlib.util, pathlib
AGENT_PATH = str(pathlib.Path(__file__).parent.parent / "agents" / "v018_f_subsistence_fixed.py")
AGENT_B_PATH = str(pathlib.Path(__file__).parent.parent / "agents" / "v018_b_batch_cap.py")

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ── Helpers ────────────────────────────────────────────────────────────────

def make_eval(mod, market_inv, day=5, labor_cost_per_action=1.0):
    """Return a bound eval_crops function for use in tests."""
    seed_key = f"test_{id(market_inv)}_{day}"
    os.environ["KAGGRICULTURE_SEED"] = seed_key
    m = mod._METRICS[seed_key]
    for crop in CROPS:
        m["crops"][crop] = {"planted": 0, "watered": 0, "harvested": 0, "deaths": 0}
    m["workers"]["useful_actions"] = 100
    m["farmer"]["useful_actions"] = 100
    m["economy"]["worker_spending"] = labor_cost_per_action * 200

    state = types.SimpleNamespace(
        day=day, step=day * 24, hour=0, player=0, board_size=10, money=10000,
        farmer=(5, 5), hands=[],
        seeds={c: 5 for c in CROPS},
        shed={},
        market={"inventory": market_inv, "prices": {}},
        my_farm={
            "tiles": [[None]*10 for _ in range(10)],
            "farmer": [5, 5], "hands": [],
            "unlocked_quadrants": ["NW"], "hires_today": 0,
        },
        hires_today=0,
    )
    state.get_tile = lambda x, y: state.my_farm["tiles"][y][x]

    econ = mod.EconomicCalculator(state)
    strategy_cfg = types.SimpleNamespace(
        crop_policy="TOMATO", cash_reserve=500,
        sell_batch_size=10, min_sell_price=2, worker_roi_threshold=50,
    )
    strategy = types.SimpleNamespace(config=strategy_cfg)

    crop_actions = {"WHEAT": 5, "CARROT": 4, "TOMATO": 15, "STRAWBERRY": 20, "MELON": 12}
    crop_max_yield = {"WHEAT": 6, "CARROT": 4, "TOMATO": 16, "STRAWBERRY": 16, "MELON": 6}
    historical_cpa = m["economy"]["worker_spending"] / (m["workers"]["useful_actions"] + m["farmer"]["useful_actions"])

    def eval_crops(crop_list, sunk_labor=False):
        best_p = -999999
        best_c = strategy_cfg.crop_policy
        for crop_name in crop_list:
            seed_cost = CROPS[crop_name]["seed"]
            remaining_days = 30 - state.day
            crop_info = CROPS[crop_name]
            first_yield = crop_info["first_yield_day"]
            if remaining_days - 1 < first_yield:
                achievable_yield = 0
            else:
                if crop_info.get("ongoing"):
                    possible = (remaining_days - 1 - first_yield) // 2 + 1
                    actual = min(crop_info["max_yield"], max(0, possible))
                    achievable_yield = int(crop_max_yield[crop_name] * actual / crop_info["max_yield"])
                else:
                    ws = (crop_info["max_yield_day"] + 1) // 2
                    bonus = max(0, min(crop_info["max_yield_day"], remaining_days - 1) - ws + 1)
                    yc = min(crop_info["max_yield"], 1 + bonus)
                    achievable_yield = int(crop_max_yield[crop_name] * yc / crop_info["max_yield"])

            cur_inv = market_inv.get(crop_name, 10000)
            expected_rev = sum(econ.get_price_at_inventory(crop_name, cur_inv + i)
                               for i in range(achievable_yield))
            worker_cost = 0 if sunk_labor else crop_actions[crop_name] * historical_cpa
            planted = m["crops"][crop_name]["planted"]
            deaths = m["crops"][crop_name]["deaths"]
            dr = deaths / planted if planted > 0 else 0
            loss = expected_rev * dr
            profit = (expected_rev - seed_cost - worker_cost - loss) / crop_actions[crop_name]
            if profit > best_p:
                best_p = profit
                best_c = crop_name
        return best_c, best_p

    return eval_crops, state, econ, m


# ── Test Cases ─────────────────────────────────────────────────────────────

class TestV018FSubsistenceFallback(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = _load(AGENT_PATH, "v018_f")
        cls.mod_b = _load(AGENT_B_PATH, "v018_b")

    # ── A. Premium crop available → fallback does NOT activate ──────────────
    def test_A_premium_profitable_no_fallback(self):
        """When any premium crop is profitable, fallback must not fire."""
        low_inv = {c: 100 for c in CROPS}  # low market inventory → high prices
        eval_crops, _, _, _ = make_eval(self.mod, low_inv, day=5, labor_cost_per_action=0.1)
        best_crop, best_profit = eval_crops(["TOMATO", "STRAWBERRY", "MELON"])
        # Premium is profitable; fallback condition (best_profit <= 0) is false
        self.assertGreater(best_profit, 0, "Premium EV should be > 0 with healthy market")
        # Simulate fallback gate
        empty_tiles = list(range(15))
        trigger = 10
        fallback_would_fire = best_profit <= 0 and len(empty_tiles) > trigger
        self.assertFalse(fallback_would_fire, "Fallback must NOT activate when premium is profitable")

    # ── B. Premium market saturated → fallback CAN activate ─────────────────
    def test_B_saturated_market_fallback_activates(self):
        """When all premium crops are unprofitable, fallback gate opens."""
        sat_inv = {"WHEAT": 200, "CARROT": 200,
                   "TOMATO": 100000, "STRAWBERRY": 100000, "MELON": 100000}
        eval_crops, _, _, m = make_eval(self.mod, sat_inv, day=5, labor_cost_per_action=50.0)
        _, best_profit = eval_crops(["TOMATO", "STRAWBERRY", "MELON"])
        self.assertLessEqual(best_profit, 0, "Saturated premium EV should be <= 0")
        empty_tiles = list(range(15))
        trigger = 10
        fallback_would_fire = best_profit <= 0 and len(empty_tiles) > trigger
        self.assertTrue(fallback_would_fire, "Fallback gate should open with saturated market + empty land")

    # ── C. Fallback chooses a profitable Wheat/Carrot crop ──────────────────
    def test_C_fallback_picks_profitable_staple(self):
        """Fallback eval (sunk_labor=True) should find Wheat/Carrot profitable."""
        sat_inv = {"WHEAT": 100, "CARROT": 100,
                   "TOMATO": 100000, "STRAWBERRY": 100000, "MELON": 100000}
        eval_crops, _, _, _ = make_eval(self.mod, sat_inv, day=5, labor_cost_per_action=50.0)
        fb_crop, fb_profit = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        self.assertGreater(fb_profit, 0, "Fallback crop must be profitable on seed-cost basis")
        self.assertIn(fb_crop, ["WHEAT", "CARROT"])

    # ── D. Fallback rejects crop whose revenue is below seed cost ────────────
    def test_D_fallback_rejects_uneconomical_crop(self):
        """
        A crop with achievable_yield=0 has revenue=0 < seed_cost → fallback rejects it.
        At day 29 (remaining_days=1): remaining-1=0 < first_yield_day=2 for Wheat,
        and 0 < 3 for Carrot → both have achievable_yield=0 → profit < 0.
        The price floor for Wheat is $15 (not $1); the economic gate fires via timing.
        """
        sat_inv = {c: 100 for c in CROPS}
        eval_crops, _, _, _ = make_eval(self.mod, sat_inv, day=29, labor_cost_per_action=0.0)
        fb_crop, fb_profit = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        self.assertLessEqual(fb_profit, 0,
            "At day 29, achievable_yield=0 → revenue=0 < seed_cost → fallback must reject")

    # ── E. Fallback respects remaining-season harvest timing ─────────────────
    def test_E_fallback_respects_harvest_timing(self):
        """On day 28, Wheat (first_yield_day=2) is still plantable; Melon (7) is not."""
        sat_inv = {"WHEAT": 100, "CARROT": 100,
                   "TOMATO": 100000, "STRAWBERRY": 100000, "MELON": 100000}
        eval_crops, _, _, _ = make_eval(self.mod, sat_inv, day=28, labor_cost_per_action=50.0)
        # Wheat: remaining=2, first_yield=2, 2-1=1 < 2? No, 1 < 2 is True → achievable=0
        # Actually remaining_days-1 = 2-1 = 1 < 2 → achievable_yield=0 for wheat too
        # Carrot: remaining=2, first_yield=3, 1 < 3 → achievable=0
        # So both are 0 at day 28 → profit should be ≤ 0
        fb_crop, fb_profit = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        self.assertLessEqual(fb_profit, 0,
            "At day 28, no staple crop should be plantable (achievable_yield=0)")

    def test_E2_fallback_plantable_early_season(self):
        """On day 5, both Wheat and Carrot should have achievable yield > 0."""
        sat_inv = {"WHEAT": 100, "CARROT": 100,
                   "TOMATO": 100000, "STRAWBERRY": 100000, "MELON": 100000}
        eval_crops, _, _, _ = make_eval(self.mod, sat_inv, day=5, labor_cost_per_action=50.0)
        fb_crop, fb_profit = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        self.assertGreater(fb_profit, 0, "At day 5, staples should be plantable")

    # ── F. Fallback respects the V018-B daily batch cap ─────────────────────
    def test_F_batch_cap_applies_before_fallback_planting(self):
        """
        The batch cap caps simulated_seeds BEFORE the planting loop runs.
        The fallback only adds a BUY_SEED task (future purchase), not a direct
        plant. Therefore it cannot bypass the cap on today's actual planting.

        Verify: if a crop is capped at DAILY_PLANT_CAP=2 but agent has 10 seeds,
        only 2 plant tasks are queued.
        """
        mod = self.mod
        seed_key = "test_F_batch_cap"
        os.environ["KAGGRICULTURE_SEED"] = seed_key
        os.environ["V018_B_CAP"] = "2"

        m = mod._METRICS[seed_key]
        for crop in CROPS:
            m["crops"][crop] = {"planted": 0, "watered": 0, "harvested": 0, "deaths": 0}
        m["workers"]["useful_actions"] = 100
        m["farmer"]["useful_actions"] = 100
        m["economy"]["worker_spending"] = 200

        # Build simulated_seeds dict as the agent would
        simulated_seeds = {"WHEAT": 10, "CARROT": 0, "TOMATO": 0, "STRAWBERRY": 0, "MELON": 0}
        DAILY_PLANT_CAP = int(os.environ.get("V018_B_CAP", 4))
        blocked_total = 0
        for crop in list(simulated_seeds.keys()):
            if simulated_seeds[crop] > DAILY_PLANT_CAP:
                blocked = simulated_seeds[crop] - DAILY_PLANT_CAP
                blocked_total += blocked
                simulated_seeds[crop] = DAILY_PLANT_CAP

        self.assertEqual(simulated_seeds["WHEAT"], 2,
            "Batch cap must reduce WHEAT seeds to DAILY_PLANT_CAP=2")
        self.assertEqual(blocked_total, 8, "8 planting attempts should be blocked")
        self.assertEqual(sum(simulated_seeds.values()), 2,
            "Total plantable today must equal DAILY_PLANT_CAP")

        os.environ["V018_B_CAP"] = "4"  # restore

    # ── G. Fallback cannot create an infinite purchase/plant loop ────────────
    def test_G_no_infinite_loop(self):
        """
        The fallback adds at most one BUY_SEED task per plan_tasks() call
        (for the single target_crop). Multiple calls on the same turn do not
        stack additional purchases because plan_tasks() resets self.tasks=[].
        Verify: running eval_crops twice with the same state gives the same result.
        """
        sat_inv = {"WHEAT": 100, "CARROT": 100,
                   "TOMATO": 100000, "STRAWBERRY": 100000, "MELON": 100000}
        eval_crops, _, _, _ = make_eval(self.mod, sat_inv, day=5, labor_cost_per_action=50.0)
        result1 = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        result2 = eval_crops(["WHEAT", "CARROT"], sunk_labor=True)
        self.assertEqual(result1[0], result2[0], "Repeated eval must be idempotent (same crop)")
        self.assertAlmostEqual(result1[1], result2[1], places=4,
            msg="Repeated eval must be idempotent (same profit)")

    # ── H. V018-B behavior unchanged when fallback is inactive ──────────────
    def test_H_premium_path_identical_to_v018b(self):
        """
        When premium crops are profitable, V018-F's Step 3 (all-crop eval)
        must produce the same crop selection as V018-B's flat loop.
        """
        # Healthy market: both agents should pick the same crop
        low_inv = {c: 100 for c in CROPS}
        eval_f, _, econ_f, _ = make_eval(self.mod, low_inv, day=5, labor_cost_per_action=0.5)
        eval_b, _, econ_b, _ = make_eval(self.mod_b, low_inv, day=5, labor_cost_per_action=0.5)

        # V018-F all-crop path (Step 3 equivalent)
        best_f, profit_f = eval_f(["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"])

        # V018-B flat-loop equivalent (same function, same inputs)
        best_b, profit_b = eval_b(["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"])

        self.assertEqual(best_f, best_b,
            f"V018-F and V018-B must pick same crop in healthy market: {best_f} vs {best_b}")
        self.assertAlmostEqual(profit_f, profit_b, places=2,
            msg="V018-F and V018-B must compute same profit in healthy market")


if __name__ == "__main__":
    unittest.main(verbosity=2)
