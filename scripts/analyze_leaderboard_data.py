import pandas as pd
import numpy as np
import os
from pathlib import Path

def run_analysis():
    csv_path = "scratch/leaderboard/kaggriculture-publicleaderboard-2026-09-01T19_00_28.csv"
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    print("=== LEADERBOARD METADATA ===")
    print("Columns:", df.columns.tolist())
    print(f"Total Rows: {len(df)}")
    print("\nSample Rows:")
    print(df.head(10))
    
    score_col = None
    for col in ["Score", "score", "PublicScore", "publicScore"]:
        if col in df.columns:
            score_col = col
            break
            
    if score_col:
        df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
        df_valid = df.dropna(subset=[score_col])
        print(f"\n=== SCORE / RATING DISTRIBUTION ({score_col}) ===")
        print(f"Count: {len(df_valid)}")
        print(f"Min: {df_valid[score_col].min()}")
        print(f"p10: {df_valid[score_col].quantile(0.10):.1f}")
        print(f"p25: {df_valid[score_col].quantile(0.25):.1f}")
        print(f"Median (p50): {df_valid[score_col].quantile(0.50):.1f}")
        print(f"p75: {df_valid[score_col].quantile(0.75):.1f}")
        print(f"p90: {df_valid[score_col].quantile(0.90):.1f}")
        print(f"p95: {df_valid[score_col].quantile(0.95):.1f}")
        print(f"p99: {df_valid[score_col].quantile(0.99):.1f}")
        print(f"Max: {df_valid[score_col].max():.1f}")
        
        print("\n=== TOP 30 LEADERBOARD ENTRIES ===")
        top30 = df_valid.sort_values(by=score_col, ascending=False).head(30)
        cols_to_show = [c for c in ["Rank", "rank", "TeamId", "teamId", "TeamName", "teamName", score_col, "SubmissionDate", "submissionDate"] if c in df.columns]
        print(top30[cols_to_show].to_string(index=False).encode('ascii', errors='replace').decode('ascii'))
        
        # Rating tiers
        print("\n=== RATING TIERS ===")
        print(f"Tier 1 (Rating >= 2800): {(df_valid[score_col] >= 2800).sum()} teams")
        print(f"Tier 2 (2400 <= Rating < 2800): {((df_valid[score_col] >= 2400) & (df_valid[score_col] < 2800)).sum()} teams")
        print(f"Tier 3 (2000 <= Rating < 2400): {((df_valid[score_col] >= 2000) & (df_valid[score_col] < 2400)).sum()} teams")
        print(f"Tier 4 (1500 <= Rating < 2000): {((df_valid[score_col] >= 1500) & (df_valid[score_col] < 2000)).sum()} teams")
        print(f"Tier 5 (1000 <= Rating < 1500): {((df_valid[score_col] >= 1000) & (df_valid[score_col] < 1500)).sum()} teams")
        print(f"Tier 6 (Rating < 1000): {(df_valid[score_col] < 1000).sum()} teams")

if __name__ == "__main__":
    run_analysis()
