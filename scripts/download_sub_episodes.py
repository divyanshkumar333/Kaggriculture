import subprocess
import os
import json

episodes = [
    103531837, 103533735, 103535975, 103538215, 103540442,
    103542685, 103544911, 103547172, 103549406, 103551628,
    103556110, 103553883
]

os.makedirs("kaggle_episodes/sub_55899068", exist_ok=True)

for ep in episodes:
    dest = f"kaggle_episodes/sub_55899068/episode-{ep}-replay.json"
    if not os.path.exists(dest):
        print(f"Downloading episode {ep}...")
        cmd = ["e:\\Setup\\kaggle\\kaggriculture\\.venv\\Scripts\\kaggle.exe", "competitions", "replay", str(ep)]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                with open(dest, "w") as f:
                    f.write(res.stdout)
                print(f"  Saved {dest} ({len(res.stdout)} bytes)")
            else:
                print(f"  Failed: {res.stderr}")
        except Exception as e:
            print(f"  Error: {e}")
