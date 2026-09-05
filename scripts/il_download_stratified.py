"""
Phase 3 Ingestion: Parallel Stratified Episode Downloader
---------------------------------------------------------
Downloads episodes across all score tiers (Tier 0 to Tier 6):
- Excludes all 31 holdout episodes from frozen.json
- Samples across all quantiles (Tier 6 top 0.1%, Tier 5 top 1%, Tier 4 top 5%, Tier 3 top 10%, Tier 2, Tier 1, Tier 0 bottom 50%)
- Downloads in parallel with 16 worker threads
"""

import os
import sys
import json
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

RESOLVE_URL = "https://huggingface.co/datasets/KiroSamurai/kaggriculture-il/resolve/main/datasets/il/episodes"

def download_episode(ep_id, target_dir):
    filename = f"{ep_id}.json.gz"
    filepath = os.path.join(target_dir, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return ep_id, "EXISTS", os.path.getsize(filepath)
    
    url = f"{RESOLVE_URL}/{filename}"
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    return ep_id, "DOWNLOADED", os.path.getsize(filepath)

def main():
    print("=== Selecting Stratified Episode Corpus for Deep Analysis ===", flush=True)

    df_index = pd.read_csv("datasets/il/index.csv")
    df_seats = pd.read_csv("datasets/il/seats.csv")
    with open("datasets/il/frozen.json", "r") as f:
        frozen = json.load(f)

    # Quarantined holdout set
    holdout_episodes = set(h["episode_id"] for h in frozen.get("holdout", []))
    print(f"Quarantined {len(holdout_episodes)} holdout episodes (Strict Zero-Leakage Guard).", flush=True)

    # Filter to engine 1.32.7
    df_valid = df_index[df_index["module_version"] == "1.32.7"].copy()
    df_valid = df_valid[~df_valid["episode_id"].isin(holdout_episodes)]
    
    # Compute max reward per episode
    df_valid["max_reward"] = df_valid[["reward0", "reward1"]].max(axis=1)

    # Quantiles:
    p50 = df_valid["max_reward"].quantile(0.50)
    p75 = df_valid["max_reward"].quantile(0.75)
    p90 = df_valid["max_reward"].quantile(0.90)
    p95 = df_valid["max_reward"].quantile(0.95)
    p99 = df_valid["max_reward"].quantile(0.99)
    p999 = df_valid["max_reward"].quantile(0.999)

    print(f"Reward Quantiles: P50=${p50:,.0f}, P75=${p75:,.0f}, P90=${p90:,.0f}, P95=${p95:,.0f}, P99=${p99:,.0f}, P99.9=${p999:,.0f}", flush=True)

    # Select stratified sample:
    t6 = df_valid[df_valid["max_reward"] >= p999] # All top 0.1%
    t5 = df_valid[(df_valid["max_reward"] >= p99) & (df_valid["max_reward"] < p999)].sample(n=min(150, len(df_valid[(df_valid["max_reward"] >= p99) & (df_valid["max_reward"] < p999)])), random_state=42)
    t4 = df_valid[(df_valid["max_reward"] >= p95) & (df_valid["max_reward"] < p99)].sample(n=100, random_state=42)
    t3 = df_valid[(df_valid["max_reward"] >= p90) & (df_valid["max_reward"] < p95)].sample(n=75, random_state=42)
    t2 = df_valid[(df_valid["max_reward"] >= p75) & (df_valid["max_reward"] < p90)].sample(n=75, random_state=42)
    t1 = df_valid[(df_valid["max_reward"] >= p50) & (df_valid["max_reward"] < p75)].sample(n=100, random_state=42)
    t0 = df_valid[df_valid["max_reward"] < p50].sample(n=100, random_state=42)

    selected = pd.concat([t6, t5, t4, t3, t2, t1, t0]).drop_duplicates(subset=["episode_id"])
    print(f"\nStratified Selection Total: {len(selected)} episodes")
    print(f"  Tier 6 (Top 0.1%): {len(t6)}")
    print(f"  Tier 5 (Top 1%):   {len(t5)}")
    print(f"  Tier 4 (Top 5%):   {len(t4)}")
    print(f"  Tier 3 (Top 10%):  {len(t3)}")
    print(f"  Tier 2 (75-90%):   {len(t2)}")
    print(f"  Tier 1 (50-75%):   {len(t1)}")
    print(f"  Tier 0 (<50%):     {len(t0)}")

    target_dir = os.path.join("datasets", "il", "episodes")
    os.makedirs(target_dir, exist_ok=True)

    ep_ids = selected["episode_id"].tolist()
    print(f"\n--- Downloading {len(ep_ids)} Stratified Episodes with 16 Workers ---", flush=True)

    completed = 0
    total = len(ep_ids)
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_episode, ep, target_dir): ep for ep in ep_ids}
        for fut in as_completed(futures):
            completed += 1
            if completed % 50 == 0 or completed == total:
                print(f"  Progress: {completed}/{total} ({completed/total*100:.1f}%)", flush=True)

    print("\n=== Stratified Download Complete! ===", flush=True)

if __name__ == "__main__":
    main()
