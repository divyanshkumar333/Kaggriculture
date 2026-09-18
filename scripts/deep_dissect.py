"""
Full replay dissection of top players.
Extracts Day 0-5 macro: hires, market ops, farm structure, money trajectory.
"""
import json
import glob

def dissect(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    steps = data.get("steps", [])
    final_p0 = steps[-1][0].get("reward", 0)
    final_p1 = steps[-1][1].get("reward", 0)
    winner = 0 if final_p0 >= final_p1 else 1
    if max(final_p0, final_p1) < 100000:
        return
    
    print(f"\n{'='*60}")
    print(f"File: {fpath}")
    print(f"  P0={final_p0:.0f}  P1={final_p1:.0f}  Winner=P{winner}")
    
    for day in range(5):
        start_step = day * 24
        end_step = start_step + 24
        print(f"\n  --- Day {day} ---")
        for s in range(start_step, min(end_step, len(steps))):
            seat_data = steps[s][winner]
            obs = seat_data["observation"]
            farm = obs["farms"][winner]
            money = farm["money"]
            action = seat_data.get("action") or {}
            market = action.get("market") or []
            if not market: continue
            hires = sum(1 for op in market if op and op[0] == "HIRE")
            non_hire = [op for op in market if op and op[0] != "HIRE"]
            hour = s - start_step
            print(f"    Hour {hour}: money=${money:.0f} hires={hires} ops={non_hire}")

def main():
    files = sorted(glob.glob("episode-110*-replay.json"))
    if not files:
        files = sorted(glob.glob("episode-*-replay.json"))
    for f in files[:5]:
        dissect(f)

if __name__ == "__main__":
    main()
