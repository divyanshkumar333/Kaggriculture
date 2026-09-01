import json

with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
    d = json.load(f)

steps = d["steps"]
print("=== TOWN SHOPS IN 162K REPLAY ===")
for day in range(30):
    obs = steps[day*24][0]["observation"]
    shops = obs.get("town", {}).get("unlocked_shops", [])
    prices = obs.get("market", {}).get("prices", {})
    inv = obs.get("market", {}).get("inventory", {})
    if day % 3 == 0:
        print(f"Day {day:2d} | Shops ({len(shops)}): {shops}")
        print(f"       Prices: {prices}")
        print(f"       Inv:    {inv}")
