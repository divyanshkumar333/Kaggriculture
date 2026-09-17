import pandas as pd
import numpy as np
import pickle
import os

def build_value_model():
    print("Loading datasets...")
    farmer_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/farmer_actions.csv')
    market_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/market_orders.csv')
    meta_df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/matches_meta.csv')
    
    # Reload the clustering logic (or just read the model)
    early_farmer = farmer_df[farmer_df['step'] <= 72]
    early_market = market_df[market_df['step'] <= 72]
    
    market_features = early_market.groupby(['episode_id', 'player', 'order_type', 'item'])['quantity'].sum().unstack(level=['order_type', 'item']).fillna(0)
    market_features.columns = [f"{col[0]}_{col[1]}" for col in market_features.columns]
    hires = early_market[early_market['order_type'] == 'HIRE'].groupby(['episode_id', 'player'])['quantity'].sum().rename("HIRES")
    farmer_features = early_farmer.groupby(['episode_id', 'player', 'action_verb', 'target_or_item']).size().unstack(level=['action_verb', 'target_or_item']).fillna(0)
    farmer_features.columns = [f"{col[0]}_{col[1]}" for col in farmer_features.columns]
    
    df = pd.concat([market_features, hires, farmer_features], axis=1).fillna(0).reset_index()
    
    with open('RESEARCH/kaggle_loop/training/models/kmeans_clusters.pkl', 'rb') as f:
        kmeans = pickle.load(f)
    with open('RESEARCH/kaggle_loop/training/models/supervised_classifier.pkl', 'rb') as f:
        clf_data = pickle.load(f)
        keep_cols = clf_data['features']
        
    # Ensure all keep_cols exist
    for col in keep_cols:
        if col not in df.columns:
            df[col] = 0
            
    X = df[keep_cols].values
    df['cluster'] = kmeans.predict(X)
    
    # Merge with meta to get winners
    # meta_df has episode_id, player_0_score, player_1_score, winner
    
    # Build match pairs
    match_data = []
    grouped = df.groupby('episode_id')
    
    for episode_id, group in grouped:
        if len(group) != 2: continue
        
        p0_cluster = group[group['player'] == 0]['cluster'].values[0]
        p1_cluster = group[group['player'] == 1]['cluster'].values[0]
        
        meta_row = meta_df[meta_df['episode_id'] == episode_id]
        if len(meta_row) == 0: continue
        p0_score = meta_row['player_0_score'].values[0]
        p1_score = meta_row['player_1_score'].values[0]
        
        p0_win = 1 if p0_score > p1_score else 0
        p1_win = 1 if p1_score > p0_score else 0
        
        match_data.append({'my_cluster': p0_cluster, 'opp_cluster': p1_cluster, 'win': p0_win})
        match_data.append({'my_cluster': p1_cluster, 'opp_cluster': p0_cluster, 'win': p1_win})
        
    match_df = pd.DataFrame(match_data)
    
    # Value model: Map (my_cluster, opp_cluster) -> P(WIN)
    win_rates = match_df.groupby(['my_cluster', 'opp_cluster'])['win'].mean().reset_index()
    print("\nEmpirical Win Rates (Model C Matrix):")
    print(win_rates)
    
    # Fallback to random chance if combination not seen
    value_matrix = {}
    for i in range(4):
        for j in range(4):
            value_matrix[(i, j)] = 0.5
            
    for _, row in win_rates.iterrows():
        value_matrix[(int(row['my_cluster']), int(row['opp_cluster']))] = row['win']
        
    os.makedirs('RESEARCH/kaggle_loop/training/models', exist_ok=True)
    with open('RESEARCH/kaggle_loop/training/models/value_matrix.pkl', 'wb') as f:
        pickle.dump(value_matrix, f)
    print("\nValue model saved.")

if __name__ == "__main__":
    build_value_model()
