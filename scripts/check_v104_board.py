from kaggle_environments import make

def log_v104_end_board():
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=False)
    env.run(["submission_v104_quote_priority.py", "pass"])
    final_state = env.steps[-1]
    me = final_state[0].observation["farms"][0]
    tiles = me["tiles"]
    
    counts = {}
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crop = t.get("crop")
                    counts[crop] = counts.get(crop, 0) + 1
                elif t.get("kind") in ["COOP", "PASTURE"] and "animal" in t:
                    an = t.get("animal")
                    counts[an] = counts.get(an, 0) + 1
                    
    print(f"V104 End Board: {counts}")
    print(f"V104 Final Cash: {final_state[0].reward}")

if __name__ == "__main__":
    log_v104_end_board()
