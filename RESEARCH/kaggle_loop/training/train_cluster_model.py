import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

def build_opponent_model():
    print("Loading datasets...")
    farmer_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/farmer_actions.csv')
    market_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/market_orders.csv')
    meta_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/matches_meta.csv')
    
    # Filter for first 72 steps (Days 0, 1, 2)
    early_farmer = farmer_df[farmer_df['step'] <= 72]
    early_market = market_df[market_df['step'] <= 72]
    
    # Pivot features per episode/player
    # 1. Market orders
    market_features = early_market.groupby(['episode_id', 'player', 'order_type', 'item'])['quantity'].sum().unstack(level=['order_type', 'item']).fillna(0)
    market_features.columns = [f"{col[0]}_{col[1]}" for col in market_features.columns]
    
    # Hires (item is NaN)
    hires = early_market[early_market['order_type'] == 'HIRE'].groupby(['episode_id', 'player'])['quantity'].sum().rename("HIRES")
    
    # 2. Farmer actions
    farmer_features = early_farmer.groupby(['episode_id', 'player', 'action_verb', 'target_or_item']).size().unstack(level=['action_verb', 'target_or_item']).fillna(0)
    farmer_features.columns = [f"{col[0]}_{col[1]}" for col in farmer_features.columns]
    
    # Combine
    df = pd.concat([market_features, hires, farmer_features], axis=1).fillna(0).reset_index()
    
    # Select important features for clustering (if they exist)
    keep_cols = [c for c in df.columns if any(k in c for k in ['BUY_SEED', 'BUY_ANIMAL', 'HIRES', 'PLANT', 'BUILD_COOP', 'BUILD_PASTURE'])]
    X = df[keep_cols].values
    
    print(f"Clustering on {len(keep_cols)} features for {len(df)} player trajectories...")
    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(X)
    
    df['cluster'] = labels
    
    # Print cluster profiles
    print("\nCluster Profiles (mean actions):")
    for c in range(4):
        print(f"\nCluster {c} (N={sum(labels==c)}):")
        profile = df[df['cluster'] == c][keep_cols].mean()
        for k, v in profile.items():
            if v > 0.5:
                print(f"  {k}: {v:.1f}")
                
    # Train supervised classifier on these clusters
    print("\nTraining Supervised Classifier...")
    # Train test split
    mask = np.random.rand(len(df)) < 0.8
    X_train, y_train = X[mask], labels[mask]
    X_test, y_test = X[~mask], labels[~mask]
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print("Test Accuracy:", accuracy_score(y_test, preds))
    
    # Save models and feature list
    os.makedirs('RESEARCH/kaggle_loop/training/models', exist_ok=True)
    with open('RESEARCH/kaggle_loop/training/models/kmeans_clusters.pkl', 'wb') as f:
        pickle.dump(kmeans, f)
    with open('RESEARCH/kaggle_loop/training/models/supervised_classifier.pkl', 'wb') as f:
        pickle.dump({'model': clf, 'features': keep_cols}, f)
        
    print("Models saved.")

if __name__ == "__main__":
    build_opponent_model()
