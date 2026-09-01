import json

with open("kaggle_episodes/episode-103388734-replay.json", "r") as f:
    data = json.load(f)

steps = data["steps"]

print("=================================================================")
print("DAY 0 STEP BY STEP ACTIONS FOR PLAYER 1")
print("=================================================================")

for t in range(24):
    s = steps[t]
    act = s[1].get("action", {})
    obs = s[0]["observation"]
    p1 = obs["farms"][1]
    
    mkt = act.get("market", [])
    farmer = act.get("farmer", [])
    hands = act.get("hands", [])
    
    print(f"Turn {t:2d} | Money: ${p1['money']} | Farmer at {p1['farmer']} | Hands: {p1['hands']}")
    if mkt: print(f"   Market: {mkt}")
    if farmer: print(f"   Farmer: {farmer}")
    if hands: print(f"   Hands:  {hands}")

print("\n=================================================================")
print("BOARD STATE AT END OF DAY 0 (PLAYER 1)")
print("=================================================================")
obs_d0_end = steps[23][0]["observation"]["farms"][1]
tiles = obs_d0_end["tiles"]

for r in range(10):
    row_str = []
    for c in range(10):
        t = tiles[r][c]
        if t is None: row_str.append(" . ")
        elif t == "LOCKED": row_str.append(" X ")
        elif isinstance(t, dict):
            kind = t.get("kind")
            if kind == "PLANT":
                crop = t.get("crop")
                row_str.append(f" {crop[0]} ")
            elif kind == "PASTURE":
                an = t.get("animal", "P")
                row_str.append(f" {an[0]} ")
            elif kind == "COOP":
                row_str.append(" G ")
            else:
                row_str.append(" ? ")
    print(f"Row {r}: " + "".join(row_str))
