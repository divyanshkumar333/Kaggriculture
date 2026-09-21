import os
import sys
import json
from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as K

def setup_market_test(p0_orders, p1_orders, p0_shed=None, p1_shed=None, p0_money=1000.0, p1_money=1000.0):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42})
    env.reset()

    # Inject shed stock directly into both players' private state
    default_shed = {p: 100 for p in K.PRODUCTS}
    p0_s = dict(default_shed if p0_shed is None else p0_shed)
    p1_s = dict(default_shed if p1_shed is None else p1_shed)

    # Initial state
    obs0 = env.state[0].observation
    obs1 = env.state[1].observation

    obs0.private["shed"] = dict(p0_s)
    obs1.private["shed"] = dict(p1_s)
    obs0.farms[0]["money"] = float(p0_money)
    obs0.farms[1]["money"] = float(p1_money)
    obs1.farms[0]["money"] = float(p0_money)
    obs1.farms[1]["money"] = float(p1_money)

    # Initial market inventory and prices
    inv_before = dict(obs0.market["inventory"])
    prices_before = dict(obs0.market["prices"])

    action0 = {"farmer": ["PASS"], "hands": [], "market": p0_orders}
    action1 = {"farmer": ["PASS"], "hands": [], "market": p1_orders}

    env.step([action0, action1])

    obs_after0 = env.state[0].observation
    m0_after = obs_after0.farms[0]["money"]
    m1_after = obs_after0.farms[1]["money"]

    p0_rev = m0_after - p0_money
    p1_rev = m1_after - p1_money

    inv_after = dict(obs_after0.market["inventory"])
    prices_after = dict(obs_after0.market["prices"])

    return {
        "p0_rev": p0_rev,
        "p1_rev": p1_rev,
        "delta": p0_rev - p1_rev,
        "prices_before": prices_before,
        "prices_after": prices_after,
        "inv_before": inv_before,
        "inv_after": inv_after,
        "p0_orders": p0_orders,
        "p1_orders": p1_orders
    }

def run_lab():
    results = {}

    print("=" * 75)
    print("KAGGRICULTURE MARKET LABORATORY: CONTROLLED EXPERIMENTS")
    print("=" * 75)

    # Experiment 1: Premium vs Bulk Queue Priority
    # P0: SELL STRAWBERRY before WHEAT
    # P1: SELL WHEAT before STRAWBERRY
    print("\n--- TEST 1: Premium Lead vs Bulk Lead (Cross-Commodity Contention) ---")
    t1 = setup_market_test(
        p0_orders=[["SELL", "STRAWBERRY", 10], ["SELL", "WHEAT", 50]],
        p1_orders=[["SELL", "WHEAT", 50], ["SELL", "STRAWBERRY", 10]]
    )
    print(f"P0 (Strawberry 1st, Wheat 2nd): Rev = ${t1['p0_rev']:,.2f}")
    print(f"P1 (Wheat 1st, Strawberry 2nd): Rev = ${t1['p1_rev']:,.2f}")
    print(f"P0 Advantage (Premium Lead):    Delta = ${t1['delta']:+,.2f}")
    results["test1_premium_vs_bulk_cross"] = t1

    # Experiment 2: Symmetric Strawberry Lead
    print("\n--- TEST 2: Symmetric Premium Lead (Both sell Strawberry in Slot 0) ---")
    t2 = setup_market_test(
        p0_orders=[["SELL", "STRAWBERRY", 10], ["SELL", "WHEAT", 50]],
        p1_orders=[["SELL", "STRAWBERRY", 10], ["SELL", "WHEAT", 50]]
    )
    print(f"P0 Rev = ${t2['p0_rev']:,.2f} | P1 Rev = ${t2['p1_rev']:,.2f} (Delta = ${t2['delta']:+,.2f})")
    results["test2_symmetric_premium_lead"] = t2

    # Experiment 3: Symmetric Bulk Lead
    print("\n--- TEST 3: Symmetric Bulk Lead (Both sell Wheat in Slot 0, Strawberry in Slot 1) ---")
    t3 = setup_market_test(
        p0_orders=[["SELL", "WHEAT", 50], ["SELL", "STRAWBERRY", 10]],
        p1_orders=[["SELL", "WHEAT", 50], ["SELL", "STRAWBERRY", 10]]
    )
    print(f"P0 Rev = ${t3['p0_rev']:,.2f} | P1 Rev = ${t3['p1_rev']:,.2f} (Delta = ${t3['delta']:+,.2f})")
    results["test3_symmetric_bulk_lead"] = t3

    # Experiment 4: Chunking Hazard (Single Batch vs Split Orders)
    # Both players sell 10 Strawberry. P0 submits 1 order of 10. P1 submits 2 orders of 5.
    print("\n--- TEST 4: Chunking Hazard: 1 Batch of 10 vs 2 Chunks of 5 ---")
    t4 = setup_market_test(
        p0_orders=[["SELL", "STRAWBERRY", 10]],
        p1_orders=[["SELL", "STRAWBERRY", 5], ["SELL", "STRAWBERRY", 5]]
    )
    print(f"P0 (1 batch of 10):  Rev = ${t4['p0_rev']:,.2f}")
    print(f"P1 (2 chunks of 5):  Rev = ${t4['p1_rev']:,.2f}")
    print(f"Chunking Delta:      Delta = ${t4['delta']:+,.2f}")
    results["test4_chunking_hazard"] = t4

    # Experiment 5: Chunking with Mixed Orders (The True V104 Failure Mode)
    # P1 has 2 small wheat orders before strawberry: [SELL WHEAT 5], [SELL WHEAT 5], [SELL STRAWBERRY 10]
    # P0 has [SELL STRAWBERRY 10], [SELL WHEAT 10]
    print("\n--- TEST 5: Duplicate Commodity Gating (The V104 Anomaly) ---")
    t5 = setup_market_test(
        p0_orders=[["SELL", "STRAWBERRY", 10], ["SELL", "WHEAT", 10]],
        p1_orders=[["SELL", "WHEAT", 5], ["SELL", "WHEAT", 5], ["SELL", "STRAWBERRY", 10]]
    )
    print(f"P0 (Sorted: Strawberry Slot 0):   Rev = ${t5['p0_rev']:,.2f}")
    print(f"P1 (Unsorted: Wheat Slots 0-1):    Rev = ${t5['p1_rev']:,.2f}")
    print(f"Ordering Penalty:                  Delta = ${t5['delta']:+,.2f}")
    results["test5_v104_duplicate_gating"] = t5

    # Experiment 6: Milk vs Wool vs Melon vs Strawberry hierarchy
    print("\n--- TEST 6: Multi-Premium Clash (Melon vs Milk vs Wool vs Strawberry) ---")
    t6 = setup_market_test(
        p0_orders=[["SELL", "MELON", 10], ["SELL", "MILK", 10], ["SELL", "WOOL", 10], ["SELL", "STRAWBERRY", 10]],
        p1_orders=[["SELL", "STRAWBERRY", 10], ["SELL", "WOOL", 10], ["SELL", "MILK", 10], ["SELL", "MELON", 10]]
    )
    print(f"P0 (Melon -> Milk -> Wool -> Strawberry): Rev = ${t6['p0_rev']:,.2f}")
    print(f"P1 (Strawberry -> Wool -> Milk -> Melon): Rev = ${t6['p1_rev']:,.2f}")
    print(f"Priority Differential:                    Delta = ${t6['delta']:+,.2f}")
    results["test6_multipremium_clash"] = t6

    # Experiment 7: Price cliff thresholds for every product
    print("\n--- TEST 7: Marginal Price Collapse per 10 Units ---")
    marginal_collapse = {}
    for prod in K.PRODUCTS:
        initial_price = K.market_price(prod, K.MARKET_PARAMS[prod]["I0"])
        rev_10 = sum(K.market_price(prod, K.MARKET_PARAMS[prod]["I0"] + i) for i in range(10))
        rev_50 = sum(K.market_price(prod, K.MARKET_PARAMS[prod]["I0"] + i) for i in range(50))
        rev_100 = sum(K.market_price(prod, K.MARKET_PARAMS[prod]["I0"] + i) for i in range(100))
        marginal_collapse[prod] = {
            "base_price": initial_price,
            "rev_10": rev_10,
            "avg_p_10": rev_10 / 10.0,
            "rev_50": rev_50,
            "avg_p_50": rev_50 / 50.0,
            "rev_100": rev_100,
            "avg_p_100": rev_100 / 100.0,
        }
        print(f"{prod:12}: Base=${initial_price:3d} | Avg@10=${rev_10/10:5.1f} | Avg@50=${rev_50/50:5.1f} | Avg@100=${rev_100/100:5.1f}")
    results["test7_marginal_collapse"] = marginal_collapse

    # Save to JSON
    with open(r"e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\market_lab\market_lab_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved market laboratory results to RESEARCH/kaggle_loop/market_lab/market_lab_results.json")

if __name__ == "__main__":
    run_lab()
