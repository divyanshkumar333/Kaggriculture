import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
import json

def get_strategy(row):
    if row['p_melons'] >= 4:
        return 'MELON'
    elif row['p_cows'] >= 1 or row['p_strawberries'] >= 2:
        return 'STRAWBERRY'
    elif row['p_hires'] >= 10:
        return 'SWARM'
    else:
        return 'UNKNOWN'

df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/features_day3.csv')

# Infer player's strategy
df['p_strategy'] = df.apply(get_strategy, axis=1)

# Keep only rows where the player WON and the strategy is known
winners = df[(df['win'] == 1) & (df['p_strategy'] != 'UNKNOWN')].copy()

# Features are the OPPONENT's visible features at day 3
X = winners[['o_hires', 'o_melons', 'o_strawberries', 'o_cows', 'o_sheep', 'o_land']]
y = winners['p_strategy']

print("Value counts of winning strategies:")
print(y.value_counts())

# Train a shallow decision tree (depth 2 or 3) so it's easily interpretable and zero-shot converted to code
clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=42)
clf.fit(X, y)

print("\nDecision Tree Rules for Best Response Strategy:")
tree_rules = export_text(clf, feature_names=list(X.columns))
print(tree_rules)

print("\nAccuracy on Winners (How well the tree captures the optimal response):", clf.score(X, y))
