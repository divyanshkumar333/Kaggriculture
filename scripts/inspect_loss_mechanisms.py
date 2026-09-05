import pandas as pd
import numpy as np

df = pd.read_csv("scratch/v025_loss_audit_table.csv")
losses = df[df["is_loss"]].copy()

print("="*80)
print(f"DETAILED ANALYSIS OF THE {len(losses)} LOSING GAMES (27.75%)")
print("="*80)

print(f"Mean V025-A Final in Losses: ${losses['v25_final'].mean():,.0f}")
print(f"Mean V023-G Final in Losses: ${losses['v23_final'].mean():,.0f}")
print(f"Mean Loss Margin: ${losses['delta'].mean():,.0f}")
print(f"Median Loss Margin: ${losses['delta'].median():,.0f}")

print("\nAverage Bank Gap (V025-A - V023-G) at Milestones during Losses:")
for col in ["gap_d5", "gap_d6", "gap_d8", "gap_d10", "gap_d15", "gap_d20", "gap_d25"]:
    print(f"  {col.upper()}: ${losses[col].mean():+,.0f}")

print("\nAsset Counts at D30 in Losses:")
print(f"  V025-A Cows: {losses['d30_v25_cows'].mean():.1f} | V023-G Cows: {losses['d30_v23_cows'].mean():.1f}")
print(f"  V025-A Straw: {losses['d30_v25_straw'].mean():.1f} | V023-G Straw: {losses['d30_v23_straw'].mean():.1f}")
print(f"  V025-A Wheat: {losses['d30_v25_wheat'].mean():.1f} | V023-G Wheat: {losses['d30_v23_wheat'].mean():.1f}")
print(f"  V025-A Feed: {losses['d30_v25_feed'].mean():.1f} | V023-G Feed: {losses['d30_v23_feed'].mean():.1f}")
print(f"  V025-A Quads: {losses['d30_v25_quads'].mean():.1f} | V023-G Quads: {losses['d30_v23_quads'].mean():.1f}")

print("\nLoss Margin Distribution:")
print(f"  Small losses (< $5,000 delta): {len(losses[losses['delta'] > -5000])} ({len(losses[losses['delta'] > -5000])/len(losses)*100:.1f}%)")
print(f"  Medium losses ($5k-$15k delta): {len(losses[(losses['delta'] <= -5000) & (losses['delta'] > -15000)])} ({len(losses[(losses['delta'] <= -5000) & (losses['delta'] > -15000)])/len(losses)*100:.1f}%)")
print(f"  Large losses (> $15k delta): {len(losses[losses['delta'] <= -15000])} ({len(losses[losses['delta'] <= -15000])/len(losses)*100:.1f}%)")

print("\nFirst Divergence Day Distribution:")
print(losses["first_div_day"].value_counts().sort_index())
