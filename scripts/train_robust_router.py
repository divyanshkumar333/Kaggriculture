import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

# 1. Load Data
print("Loading data...")
meta = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/matches_meta.csv', encoding='utf-8', encoding_errors='ignore')
orders = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/market_orders.csv')

# 2. Extract Early Game Features (up to Turn 72 = Day 3)
print("Extracting early game features...")
early_orders = orders[orders['step'] <= 72].copy()

# Count seeds/animals bought
buys = early_orders[early_orders['order_type'].isin(['BUY_SEED', 'BUY_ANIMAL'])].copy()
buy_pivot = buys.pivot_table(index=['episode_id', 'player'], columns='item', values='quantity', aggfunc='sum').fillna(0)

# 3. Define Strategy Classes based on full game data
# We can look at what they sold most over the whole game to classify their strategy
sells = orders[orders['order_type'] == 'SELL'].copy()
sell_pivot = sells.pivot_table(index=['episode_id', 'player'], columns='item', values='quantity', aggfunc='sum').fillna(0)

def classify_strategy(row):
    melons = row.get('MELON', 0)
    strawberries = row.get('STRAWBERRY', 0)
    cows = row.get('COW', 0) # if they bought cows, they sell milk
    milk = row.get('MILK', 0)
    
    if melons > strawberries and melons > milk:
        return 'MELON'
    elif strawberries > melons and strawberries > milk:
        return 'STRAWBERRY'
    elif milk > melons and milk > strawberries:
        return 'COW'
    else:
        return 'MIXED'

sell_pivot['strategy'] = sell_pivot.apply(classify_strategy, axis=1)

# 4. Build Dataset
records = []
for _, match in meta.iterrows():
    ep = match['episode_id']
    winner = match['winner']
    
    for p in [0, 1]:
        o = 1 - p
        
        # Did p win?
        p_str = f"Player {p}"
        win = 1 if winner == p_str else 0
        
        # Player Strategy
        try:
            p_strat = sell_pivot.loc[(ep, p), 'strategy']
        except KeyError:
            p_strat = 'UNKNOWN'
            
        # Opponent early features
        try:
            o_buys = buy_pivot.loc[(ep, o)]
            o_melons = o_buys.get('MELON', 0)
            o_strawberries = o_buys.get('STRAWBERRY', 0)
            o_cows = o_buys.get('COW', 0)
        except KeyError:
            o_melons = 0
            o_strawberries = 0
            o_cows = 0
            
        records.append({
            'win': win,
            'p_strategy': p_strat,
            'o_melons': o_melons,
            'o_strawberries': o_strawberries,
            'o_cows': o_cows
        })

df = pd.DataFrame(records)

# Filter for matches where we know the strategy
df = df[df['p_strategy'] != 'UNKNOWN']

print(f"\nExtracted {len(df)} player records.")
print("\nWin Rates by Strategy:")
print(df.groupby('p_strategy')['win'].mean())

# 5. Train Model to predict Win from (Opponent Features + Our Strategy)
# Wait, a better way: for each opponent profile, which strategy wins most?
# Let's train a Decision Tree on the Winners only, to predict the strategy they used!
winners = df[df['win'] == 1].copy()

if len(winners) > 0:
    X = winners[['o_melons', 'o_strawberries', 'o_cows']]
    y = winners['p_strategy']
    
    print("\nWinner Strategy Distribution:")
    print(y.value_counts())
    
    clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=10, random_state=42)
    clf.fit(X, y)
    
    print("\nDecision Tree Rules for Optimal Response Strategy:")
    print(export_text(clf, feature_names=list(X.columns)))
    
    print(f"\nAccuracy on Winners: {clf.score(X, y):.3f}")
else:
    print("No winners found!")
