import zipfile
import pandas as pd
import json
import os
import subprocess
from pathlib import Path

def analyze_leaderboard():
    zip_path = "scratch/kaggriculture.zip"
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("scratch/leaderboard")
        
        csv_files = list(Path("scratch/leaderboard").glob("*.csv"))
        print(f"Extracted CSV files: {csv_files}")
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            print(f"\n--- {csv_file.name} (Shape: {df.shape}) ---")
            print(df.head(20))
            print(df.describe())
            print("\nTop 15 Teams:")
            if "Score" in df.columns or "score" in df.columns:
                score_col = "Score" if "Score" in df.columns else "score"
                print(df.sort_values(by=score_col, ascending=False).head(15))

def download_all_episodes():
    episodes = [
        104572125, 104531006, 104499094, 104459945, 104326323, 104152294, 
        104145292, 104100689, 103979994, 103980259, 103819550, 103766033, 
        103652122, 103614224, 103569571, 103567313, 103565071, 103562846, 
        103560587, 103558339, 103553883, 103556110, 103551628, 103549406, 
        103547172, 103544911, 103542685, 103540442, 103538215, 103535975, 
        103533735, 103531837
    ]
    os.makedirs("kaggle_episodes/sub_55899068", exist_ok=True)
    kaggle_exe = "e:\\Setup\\kaggle\\kaggriculture\\.venv\\Scripts\\kaggle.exe"
    
    for ep in episodes:
        dest = f"kaggle_episodes/sub_55899068/episode-{ep}-replay.json"
        if not os.path.exists(dest) or os.path.getsize(dest) < 1000:
            print(f"Downloading episode {ep}...")
            cmd = [kaggle_exe, "competitions", "replay", str(ep)]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    with open(dest, "w") as f:
                        f.write(res.stdout)
                    print(f"  Saved {dest} ({len(res.stdout)} bytes)")
                else:
                    print(f"  Failed {ep}: {res.stderr[:200]}")
            except Exception as e:
                print(f"  Error {ep}: {e}")

if __name__ == "__main__":
    analyze_leaderboard()
    download_all_episodes()
