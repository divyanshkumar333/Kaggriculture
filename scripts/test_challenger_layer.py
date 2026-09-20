import os
import sys
sys.path.insert(0, os.path.abspath("."))
from kaggle_environments import make
from scripts.tournament_population import load_agent
from scripts.fast_tournament import run_fast_tournament

def wrap_with_community_reflexes(base_agent_func):
    def gated_agent(obs, config=None):
        action = base_agent_func(obs, config)
        if not isinstance(action, dict):
            return action
            
        try:
            player = int(obs["player"])
            farm = obs["farms"][player]
            priv = obs["private"]
            day = int(obs.get("day", int(obs.get("step", 0)) // 24))
            tiles = farm["tiles"]
            
            farmer_act = action.get("farmer") or ["PASS"]
            hands_acts = list(action.get("hands") or [])
            units = [farmer_act] + hands_acts
            
            positions = [farm["farmer"]] + list(farm["hands"] or [])
            inventories = list(priv.get("inventories") or [])
            
            modified = False
            for i in range(min(len(units), len(positions))):
                cmd = units[i]
                if not (isinstance(cmd, list) and cmd):
                    continue
                pos = positions[i]
                x, y = int(pos[0]), int(pos[1])
                if not (0 <= x < 10 and 0 <= y < 10):
                    continue
                tile = tiles[y][x]
                inv = inventories[i] if i < len(inventories) else {}
                
                # 1. CARE GATING REFLEX
                if cmd[0] == "CARE":
                    if isinstance(tile, dict) and "animal" in tile:
                        fed = tile.get("fed_today", False)
                        held = tile.get("yield_units", 0)
                        bonus = tile.get("pending_care_bonus", 0)
                        
                        # Case A: Animal NOT fed yet today
                        if not fed:
                            if inv.get("WHEAT", 0) > 0:
                                # Upgrade to FEED immediately!
                                units[i] = ["FEED"]
                                modified = True
                            elif held >= 1:
                                units[i] = ["HARVEST"]
                                modified = True
                                
                        # Case B: Animal bonus already at cap (>= 5)
                        elif held + bonus >= 5:
                            if held >= 1:
                                units[i] = ["HARVEST"]
                                modified = True
                                
                # 2. FERTILIZE REDUNDANCY REFLEX
                elif cmd[0] == "FERTILIZE":
                    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                        fert_until = tile.get("fertilized_until_day", -1)
                        if fert_until >= day + 2:
                            # Tile is already fertilized!
                            if not tile.get("watered_today", False):
                                units[i] = ["WATER"]
                                modified = True
                            elif tile.get("yield_units", 0) >= 1:
                                units[i] = ["HARVEST"]
                                modified = True
                                
            if modified:
                action = dict(action)
                action["farmer"] = units[0]
                action["hands"] = units[1:]
        except Exception:
            pass
            
        return action
        
    return gated_agent

if __name__ == "__main__":
    # Test head-to-head: gated agent vs base agent
    base_code_path = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    base_agent = load_agent(base_code_path)
    gated_agent = wrap_with_community_reflexes(base_agent)
    
    seeds = [42, 101, 2024, 777, 9999, 1234, 5678, 9876, 1111, 2222]
    print(f"Testing Gated Reflex Layer vs Base 2945 across {len(seeds)*2} matches...")
    
    wins = 0
    losses = 0
    draws = 0
    margins = []
    
    for s in seeds:
        # Seat 0
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([gated_agent, base_agent])
        last = env.steps[-1]
        m0 = last[0]["reward"] - last[1]["reward"]
        margins.append(m0)
        if m0 > 0: wins += 1
        elif m0 < 0: losses += 1
        else: draws += 1
        print(f"Seed {s:5d} | P0: {last[0]['reward']:7.0f} vs {last[1]['reward']:7.0f} | Margin: {m0:+7.0f}")
        
        # Seat 1
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run([base_agent, gated_agent])
        last = env.steps[-1]
        m1 = last[1]["reward"] - last[0]["reward"]
        margins.append(m1)
        if m1 > 0: wins += 1
        elif m1 < 0: losses += 1
        else: draws += 1
        print(f"Seed {s:5d} | P1: {last[1]['reward']:7.0f} vs {last[0]['reward']:7.0f} | Margin: {m1:+7.0f}")
        
    print("=" * 60)
    wr = (wins / len(margins)) * 100
    avg_m = sum(margins) / len(margins)
    print(f"RESULT: {wins}W - {losses}L - {draws}D ({wr:.1f}%) | Mean Margin: {avg_m:+7.0f}")
