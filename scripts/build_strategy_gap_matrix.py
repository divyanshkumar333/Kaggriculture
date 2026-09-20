import sys
import json
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def load_agent(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("_agent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _safe(fn, obs, cfg):
    try:
        try:
            return fn(obs, cfg)
        except TypeError:
            return fn(obs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        farm = (obs.get("farms") or [{}])[obs.get("player", 0)]
        return {"farmer": ["PASS"],
                "hands": [["PASS"] for _ in (farm.get("hands") or [])],
                "market": []}

def extract_metrics(state, player_idx):
    farm = state["farms"][player_idx]
    
    workers = len(farm.get("hands", []))
    cash = farm.get("money", 0)
    
    cows = 0
    sheep = 0
    geese = 0
    crop_area = 0
    
    for row in farm.get("tiles", []):
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crop_area += 1
                elif t.get("kind") == "PASTURE" and t.get("animal") == "COW":
                    cows += 1
                elif t.get("kind") == "PASTURE" and t.get("animal") == "SHEEP":
                    sheep += 1
                elif t.get("kind") == "COOP" and t.get("animal") == "GOOSE":
                    geese += 1
                    
    land = len(farm.get("unlocked_quadrants", []))
    
    return {
        "workers": workers,
        "cash": cash,
        "cows": cows,
        "sheep": sheep,
        "geese": geese,
        "crop_area": crop_area,
        "land": land
    }

def main():
    import os
    from contextlib import redirect_stdout, redirect_stderr
    from kaggle_environments import make

    agents_to_test = [
        "agents/v025_a_aggressive_cows.py",
        "agents/v057_generalized_spoiler.py"
    ]
    
    champion = "main.py"
    
    champ_mod = load_agent(champion)
    
    checkpoints = [0, 6*24, 12*24, 24*24, 27*24] # Days 0, 6, 12, 24, 27
    
    rows = []
    
    for opp_path in agents_to_test:
        opp_mod = load_agent(opp_path)
        
        env = make("kaggriculture", configuration={"randomSeed": 42}, debug=False)
        
        print(f"Simulating {champion} vs {opp_path}...")
        env.run([lambda o, c: _safe(champ_mod.agent, o, c),
                 lambda o, c: _safe(opp_mod.agent, o, c)])
        
        steps = env.steps
        
        for cp in checkpoints:
            if cp >= len(steps):
                break
                
            state = steps[cp][0]["observation"]
            
            p0_metrics = extract_metrics(state, 0)
            p1_metrics = extract_metrics(state, 1)
            
            day = cp // 24
            
            rows.append({
                "Opponent": Path(opp_path).stem,
                "Day": day,
                "Champ_Workers": p0_metrics["workers"],
                "Opp_Workers": p1_metrics["workers"],
                "Champ_Cows": p0_metrics["cows"],
                "Opp_Cows": p1_metrics["cows"],
                "Champ_CropArea": p0_metrics["crop_area"],
                "Opp_CropArea": p1_metrics["crop_area"],
                "Champ_Cash": p0_metrics["cash"],
                "Opp_Cash": p1_metrics["cash"]
            })
            
    out_path = ROOT / "RESEARCH" / "STRATEGY_GAP_MATRIX.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Saved Strategy Gap Matrix to {out_path}")
    
if __name__ == "__main__":
    main()
