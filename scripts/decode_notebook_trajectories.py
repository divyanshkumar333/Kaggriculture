import json
import base64
import zlib
import re
from pathlib import Path

def extract_actions_from_file(filepath, var_name="_ACTIONS"):
    content = Path(filepath).read_text(encoding="utf-8")
    
    if "_AGENT_B85_PARTS" in content or "c-rk<O>Y}nlKd|^^I" in content:
        # V27 main.txt format
        match = re.search(r'\(?\s*\'(c-.*?)\'\s*\)', content, re.DOTALL)
        if match:
            b85_str = match.group(1).replace("'\n    '", "").replace("'\n    '", "")
            # Just extract all strings inside quotes that look like base85 and join them
            strings = re.findall(r"'([^']+)'", content)
            b85_str = "".join([s for s in strings if len(s) > 20 and not s.endswith(".py")])
            try:
                raw = zlib.decompress(base64.b85decode(b85_str.encode("ascii")))
                return json.loads(raw.decode("utf-8"))
            except Exception as e:
                pass
            
            # Alternative: try parsing _LEGACY_ACTIONS string parts directly from main.txt
            parts = []
            for line in content.split("\n"):
                if line.strip().startswith("'") and line.strip().endswith("'"):
                    parts.append(line.strip()[1:-1])
            b85_str = "".join(parts)
            try:
                raw = zlib.decompress(base64.b85decode(b85_str.encode("ascii")))
                return json.loads(raw.decode("utf-8"))
            except:
                pass

    # Try V16 format
    match = re.search(r"b85decode\('([^']+)'", content)
    if match:
        b85_str = match.group(1)
        try:
            raw = zlib.decompress(base64.b85decode(b85_str.encode("ascii")))
            return json.loads(raw.decode("utf-8"))
        except:
            pass
            
    return []

def analyze_trajectory(actions, name):
    print(f"\n{'='*50}\nANALYSIS FOR: {name}\n{'='*50}")
    
    cows = 0
    sheep = 0
    hires_by_day = {}
    crops_planted = {}
    
    for step, action in enumerate(actions):
        day = step // 24
        
        market = action.get("market", [])
        for order in market:
            if order[0] == "BUY_ANIMAL":
                if order[1] == "COW":
                    cows += int(order[2])
                    print(f"Day {day}, Step {step}: Bought {order[2]} COW (Total: {cows})")
                elif order[1] == "SHEEP":
                    sheep += int(order[2])
                    print(f"Day {day}, Step {step}: Bought {order[2]} SHEEP (Total: {sheep})")
            elif order[0] == "HIRE":
                hires_by_day[day] = hires_by_day.get(day, 0) + 1
            elif order[0] == "BUY_LAND":
                print(f"Day {day}, Step {step}: Bought Land")
                
        all_unit_actions = [action.get("farmer", ["PASS"])] + action.get("hands", [])
        for u_action in all_unit_actions:
            if u_action and u_action[0] == "PLANT":
                crop = u_action[1]
                crops_planted[crop] = crops_planted.get(crop, 0) + 1
                
    print(f"\nFinal Livestock: {cows} COW, {sheep} SHEEP")
    print(f"Total Crops Planted: {crops_planted}")
    
    print("\nLabor Schedule (First 10 days):")
    for d in range(10):
        print(f"Day {d}: {hires_by_day.get(d, 0)} Hires")
        
    print("\nLabor Schedule (Midgame Days 10-20):")
    for d in range(10, 20):
        print(f"Day {d}: {hires_by_day.get(d, 0)} Hires")

if __name__ == "__main__":
    v16_actions = extract_actions_from_file("scratch_v16.py")
    if v16_actions:
        analyze_trajectory(v16_actions, "V16-RC5")
    else:
        print("Failed to extract V16")
        
    v27_actions = extract_actions_from_file("up/New folder/main.txt")
    if v27_actions:
        analyze_trajectory(v27_actions, "V27 Midgame Meta Reset")
    else:
        print("Failed to extract V27")
