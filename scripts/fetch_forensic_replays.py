"""
Forensic replay fetcher for V104 and V105.
Downloads replay JSON, extracts winner/loser/cash/opponents/divergence.
"""
import subprocess, json, os, sys, re
from pathlib import Path

OUT_DIR = Path(r"e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# V104 submission ID: 56417252 — top episodes
V104_EPISODES = [
    113186913, 113177346, 113162217, 113161594, 113146367,
    113138783, 113129899, 113126811, 113112280, 113101893,
    113094106, 113081440, 113080112, 113071683, 113070698,
    113061188, 113049768, 113037951, 113038018, 113036067,
]

# V105 submission ID: 56554487 — all episodes (only 10 played)
V105_EPISODES = [
    113352265, 113351139, 113349978, 113348839, 113347713,
    113346568, 113345407, 113344258, 113343122, 113341974,
]

def fetch_replay(ep_id):
    dest = OUT_DIR / f"replay_{ep_id}.json"
    if dest.exists():
        return dest
    r = subprocess.run(
        [sys.executable, "-m", "kaggle", "competitions", "replay", str(ep_id), "-p", str(OUT_DIR)],
        capture_output=True, text=True
    )
    # kaggle CLI saves as <ep_id>.json
    candidates = list(OUT_DIR.glob(f"*{ep_id}*"))
    if candidates:
        return candidates[0]
    return None

def parse_replay(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}

    # kaggle-environments replay JSON structure
    info = {"episode_id": path.stem.split("_")[-1]}
    steps = data.get("steps", [])
    if not steps:
        return info

    # Final step rewards
    final = steps[-1]
    rewards = [s.get("reward") for s in final]
    info["rewards"] = rewards
    info["winner"] = 0 if (rewards[0] or 0) > (rewards[1] or 0) else 1

    # Observation from last step - check agent statuses
    obs_agents = [s.get("observation", {}) for s in final]
    info["statuses"] = [s.get("status") for s in final]

    # Opening: Day 0 market orders
    if len(steps) > 1:
        opening = steps[1]
        actions = [s.get("action", {}) for s in opening]
        info["opening_markets"] = [a.get("market", []) for a in actions]

    # Cash trajectory — sample final obs
    try:
        last_obs = steps[-1][0].get("observation", {})
        farms = last_obs.get("farms", [])
        info["final_cash"] = [f.get("money") for f in farms]
    except Exception:
        pass

    # Midgame sample at step 360 (day 15)
    if len(steps) > 360:
        mid = steps[360]
        try:
            obs = mid[0].get("observation", {})
            farms = obs.get("farms", [])
            info["midgame_cash_day15"] = [f.get("money") for f in farms]
        except Exception:
            pass

    return info

print("Fetching V104 replays...")
v104_results = []
for ep in V104_EPISODES:
    print(f"  Episode {ep}...")
    path = fetch_replay(ep)
    if path:
        parsed = parse_replay(path)
        parsed["episode_id"] = ep
        v104_results.append(parsed)
        print(f"    Rewards: {parsed.get('rewards')} Winner: P{parsed.get('winner')} Cash: {parsed.get('final_cash')}")
    else:
        print(f"    FETCH FAILED")

print("\nFetching V105 replays...")
v105_results = []
for ep in V105_EPISODES:
    print(f"  Episode {ep}...")
    path = fetch_replay(ep)
    if path:
        parsed = parse_replay(path)
        parsed["episode_id"] = ep
        v105_results.append(parsed)
        print(f"    Rewards: {parsed.get('rewards')} Winner: P{parsed.get('winner')} Cash: {parsed.get('final_cash')}")
    else:
        print(f"    FETCH FAILED")

# Summary
print("\n=== V104 SUMMARY ===")
v104_wins = sum(1 for r in v104_results if r.get("winner") == 0 or (r.get("rewards", [0,0])[0] or 0) > (r.get("rewards",[0,0])[1] or 0))
print(f"Episodes analyzed: {len(v104_results)}, Wins (as P0): {v104_wins}")

print("\n=== V105 SUMMARY ===")
v105_wins = sum(1 for r in v105_results if r.get("winner") == 0 or (r.get("rewards", [0,0])[0] or 0) > (r.get("rewards",[0,0])[1] or 0))
print(f"Episodes analyzed: {len(v105_results)}, Wins (as P0): {v105_wins}")

# Save summary
summary = {"V104_episodes": v104_results, "V105_episodes": v105_results}
(OUT_DIR / "replay_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"\nSaved to {OUT_DIR / 'replay_summary.json'}")
