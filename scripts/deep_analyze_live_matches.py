import json
import glob
import os

files = sorted(glob.glob("kaggle_episodes/sub_55899068/episode-*-replay.json"))

print("================================================================================")
print(f"ANALYSIS OF ALL {len(files)} LIVE KAGGLE MATCHES FOR SUBMISSION 55899068 (V020-C)")
print("================================================================================")

results = []

for fpath in files:
    with open(fpath, "r") as f:
        data = json.load(f)
        
    ep_id = os.path.basename(fpath).split("-")[1]
    steps = data["steps"]
    final_step = steps[-1]
    
    p0_rew = final_step[0].get("reward", 0)
    p1_rew = final_step[1].get("reward", 0)
    
    # Identify which player index was our V020-C
    # In V020-C, we plant Melons on Day 0-1, 1 worker, no animals.
    # Let's inspect step 10
    obs10 = steps[10 * 24 + 1][0]["observation"]
    f0_animals = sum(1 for r in obs10["farms"][0]["tiles"] for t in r if isinstance(t, dict) and t.get("animal"))
    f1_animals = sum(1 for r in obs10["farms"][1]["tiles"] for t in r if isinstance(t, dict) and t.get("animal"))
    
    # Check melons
    f0_melons = sum(1 for r in obs10["farms"][0]["tiles"] for t in r if isinstance(t, dict) and t.get("crop") == "MELON")
    f1_melons = sum(1 for r in obs10["farms"][1]["tiles"] for t in r if isinstance(t, dict) and t.get("crop") == "MELON")
    
    # Check which player has the V020-C signature (no animals, 20+ melons or strawberries)
    if f0_animals == 0 and f1_animals > 0:
        our_p = 0
        opp_p = 1
    elif f1_animals == 0 and f0_animals > 0:
        our_p = 1
        opp_p = 0
    else:
        # Check hands or other
        our_p = 0 if len(obs10["farms"][0].get("hands", [])) <= 1 else 1
        opp_p = 1 - our_p
        
    our_rew = p0_rew if our_p == 0 else p1_rew
    opp_rew = p1_rew if our_p == 0 else p0_rew
    won = our_rew > opp_rew
    
    # Analyze opponent end-game state (Day 25)
    obs25 = steps[25 * 24 + 1][0]["observation"]
    opp_farm = obs25["farms"][opp_p]
    opp_hands = len(opp_farm.get("hands", []))
    opp_quads = len(opp_farm.get("unlocked_quadrants", []))
    
    opp_plants = {}
    opp_animals = {}
    for r in opp_farm["tiles"]:
        for t in r:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    c = t.get("crop")
                    opp_plants[c] = opp_plants.get(c, 0) + 1
                elif t.get("animal"):
                    a = t.get("animal")
                    opp_animals[a] = opp_animals.get(a, 0) + 1
                    
    our_farm = obs25["farms"][our_p]
    our_plants = {}
    for r in our_farm["tiles"]:
        for t in r:
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                c = t.get("crop")
                our_plants[c] = our_plants.get(c, 0) + 1
                
    results.append({
        "ep_id": ep_id,
        "our_p": our_p,
        "our_rew": our_rew,
        "opp_rew": opp_rew,
        "won": won,
        "opp_hands": opp_hands,
        "opp_quads": opp_quads,
        "opp_plants": opp_plants,
        "opp_animals": opp_animals,
        "our_plants": our_plants
    })
    
    outcome = "WIN " if won else "LOSS"
    delta = our_rew - opp_rew
    print(f"Ep {ep_id:9s} | {outcome} | Ours: ${our_rew:7,.0f} vs Opp: ${opp_rew:7,.0f} (Delta: ${delta:+7,.0f}) | OppHands: {opp_hands:2d} | OppQuads: {opp_quads} | OppAnim: {opp_animals} | OppCrops: {opp_plants}")

print("-" * 120)
total_wins = sum(1 for r in results if r["won"])
total_losses = len(results) - total_wins
print(f"SUMMARY: {total_wins} Wins / {total_losses} Losses (Win Rate: {(total_wins/len(results))*100:.1f}%)")
print(f"Our Mean Score: ${sum(r['our_rew'] for r in results)/len(results):,.0f}")
print(f"Opp Mean Score: ${sum(r['opp_rew'] for r in results)/len(results):,.0f}")
