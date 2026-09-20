import csv
import subprocess
import os

os.makedirs('RESEARCH/live/replays', exist_ok=True)

episodes = []
with open('RESEARCH/live/v099_episodes.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        episodes.append(row['id'])

print(f"Found {len(episodes)} episodes.")

for ep_id in episodes[:5]:  # Just do first 5 for now
    print(f"Downloading replay for {ep_id}...")
    subprocess.run(['.venv\Scripts\kaggle.exe', 'competitions', 'replay', ep_id, '-p', 'RESEARCH/live/replays'], check=True)
