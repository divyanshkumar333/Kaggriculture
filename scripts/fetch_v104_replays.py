import os
import subprocess
import time
import json
import csv
from pathlib import Path

# V104 submission ID
SUBMISSION_ID = 56417252

# Create output dir
out_dir = Path("RESEARCH/kaggle_loop/kaggle_forensics/v104")
out_dir.mkdir(parents=True, exist_ok=True)
replays_dir = out_dir / "replays"
replays_dir.mkdir(exist_ok=True)
logs_dir = out_dir / "logs"
logs_dir.mkdir(exist_ok=True)

# Fetch episodes (csv format)
print(f"Fetching episodes for {SUBMISSION_ID}...")
subprocess.run([
    ".venv\\Scripts\\python.exe", "-m", "kaggle", "competitions", "episodes", 
    str(SUBMISSION_ID), "-v"
], stdout=open(out_dir / "episodes.csv", "w"))

print("Parsing episodes...")
episodes = []
with open(out_dir / "episodes.csv", "r") as f:
    # Read CSV
    lines = f.readlines()
    if not lines:
        print("No episodes found or failed to fetch.")
        exit(1)
        
    reader = csv.DictReader(lines)
    for row in reader:
        episodes.append(row)

print(f"Found {len(episodes)} episodes.")

# Download the most recent 10 replays for analysis
for i, ep in enumerate(episodes[:10]):
    ep_id = ep['id']
    print(f"Downloading replay {ep_id} ({i+1}/10)...")
    subprocess.run([
        ".venv\\Scripts\\python.exe", "-m", "kaggle", "competitions", "replay",
        str(ep_id), "-p", str(replays_dir)
    ])
    
    # Optional: try to fetch logs for player 0 and 1
    # subprocess.run([
    #     ".venv\\Scripts\\python.exe", "-m", "kaggle", "competitions", "logs",
    #     str(ep_id), "0", "-p", str(logs_dir)
    # ])
    # subprocess.run([
    #     ".venv\\Scripts\\python.exe", "-m", "kaggle", "competitions", "logs",
    #     str(ep_id), "1", "-p", str(logs_dir)
    # ])
    time.sleep(1)

print("Done downloading replays.")
