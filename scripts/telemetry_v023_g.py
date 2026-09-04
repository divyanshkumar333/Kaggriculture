import importlib.util
import json
import pandas as pd
import numpy as np
from kaggle_environments import make

def load_agent(path):
    spec = importlib.util.spec_from_file_location("agent_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def run_telemetry(seeds=[1200, 1201, 1202, 1203, 1204]):
    agent_v023_g = load_agent("agents/v023_g_capital_optimizer.py")
    agent_v022_c = load_agent("agents/v022_c_market_batching.py")
    
    all_seed_stats = []
    
    for s in seeds:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=False)
        env.reset()
        
        daily_records = []
        step = 0
        
        while not env.done and step < 720:
            obs = env.state[0].observation
            p0_obs = {
                "player": 0,
                "step": step,
                "day": obs["day"],
                "hour": obs["hour"],
                "farms": obs["farms"],
                "private": obs["private"],
                "market": obs["market"],
                "town": obs["town"],
            }
            p1_obs = {
                "player": 1,
                "step": step,
                "day": obs["day"],
                "hour": obs["hour"],
                "farms": obs["farms"],
                "private": obs["private"],
                "market": obs["market"],
                "town": obs["town"],
            }
            
            day = obs["day"]
            hour = obs["hour"]
            
            # Extract state metrics at hour 0 of each day
            if hour == 0 and day >= 15:
                p0_farm = obs["farms"][0]
                p0_priv = obs["private"]
                tiles = p0_farm["tiles"]
                
                n_straw = 0
                n_wheat = 0
                n_melon = 0
                n_cows = 0
                n_sheep = 0
                n_empty = 0
                n_weeds = 0
                n_decaying_straw = 0
                
                for r in range(10):
                    for c in range(10):
                        t = tiles[r][c]
                        if t is None:
                            n_empty += 1
                        elif isinstance(t, dict):
                            k = t.get("kind")
                            if k == "WEED":
                                n_weeds += 1
                            elif k == "PLANT":
                                crop = t.get("crop")
                                yu = t.get("yield_units", 0)
                                age = day - t.get("planted_day", day)
                                if crop == "STRAWBERRY":
                                    n_straw += 1
                                    if age >= 10:
                                        n_decaying_straw += 1
                                elif crop == "WHEAT":
                                    n_wheat += 1
                                elif crop == "MELON":
                                    n_melon += 1
                            elif k in ["COOP", "PASTURE"]:
                                an = t.get("animal")
                                if an == "COW": n_cows += 1
                                elif an == "SHEEP": n_sheep += 1
                                
                daily_records.append({
                    "seed": s,
                    "day": day,
                    "money": p0_farm["money"],
                    "hands": len(p0_farm["hands"]),
                    "strawberries": n_straw,
                    "decaying_straw": n_decaying_straw,
                    "wheat": n_wheat,
                    "empty": n_empty,
                    "weeds": n_weeds,
                    "cows": n_cows,
                    "sheep": n_sheep,
                    "wheat_seeds": p0_priv["seeds"].get("WHEAT", 0),
                    "straw_seeds": p0_priv["seeds"].get("STRAWBERRY", 0),
                    "shed_wheat": p0_priv["shed"].get("WHEAT", 0),
                    "shed_straw": p0_priv["shed"].get("STRAWBERRY", 0),
                    "shed_milk": p0_priv["shed"].get("MILK", 0),
                })
                
            a0 = agent_v023_g(p0_obs)
            a1 = agent_v022_c(p1_obs)
            env.step([a0, a1])
            step += 1
            
        all_seed_stats.extend(daily_records)
        
    df = pd.DataFrame(all_seed_stats)
    mean_df = df.groupby("day").mean().reset_index()
    print("=== V023-G TELEMETRY (DAYS 15-29 MEAN ACROSS SEEDS) ===")
    print(mean_df[["day", "money", "strawberries", "decaying_straw", "wheat", "empty", "weeds", "wheat_seeds", "cows", "shed_milk", "shed_straw"]].to_string(index=False))
    return df

if __name__ == "__main__":
    df = run_telemetry([1200, 1201, 1202, 1203, 1204])
