from kaggle_environments import make

def run_experiment():
    print("=== TILE USAGE TRACE ===")
    
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run(["agents/014_robust_trace.py", "agents/014_robust_trace.py"])
    
    used_tiles = set()
    
    for step in env.steps:
        obs = step[0].observation
        me = obs["farms"][0]
        for y in range(10):
            for x in range(10):
                t = me["tiles"][y][x]
                if t is not None and t != "LOCKED":
                    used_tiles.add((x, y))
                    
    print("Tiles used by 014:")
    for y in range(10):
        row = ""
        for x in range(10):
            if (x, y) in used_tiles:
                row += "[X]"
            elif x < 5 and y < 5:
                row += "[ ]"
            else:
                row += " . "
        print(row)
        
    print(f"Total used: {len(used_tiles)}")

if __name__ == "__main__":
    run_experiment()
