import glob
import json
import os

def check_replays():
    replays = glob.glob("episode-*.json")
    print(f"Found {len(replays)} episode replays.")
    
    total_steps = 0
    engine_versions = set()
    features = set()
    
    for r in replays:
        with open(r, "r") as f:
            data = json.load(f)
        
        info = data.get("info", {})
        engine_versions.add(info.get("version", "unknown"))
        
        steps = data.get("steps", [])
        total_steps += len(steps)
        
        if len(steps) > 0:
            obs = steps[0][0].get("observation", {})
            if isinstance(obs, str):
                try:
                    obs = json.loads(obs)
                except:
                    pass
            features.update(obs.keys())
            
    print(f"Total Steps: {total_steps}")
    print(f"Engine Versions: {list(engine_versions)}")
    print(f"Available Observation Keys: {list(features)}")

if __name__ == "__main__":
    check_replays()
