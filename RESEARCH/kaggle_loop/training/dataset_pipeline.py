import pandas as pd
import numpy as np

def extract_features(meta_path, market_path, max_step=72):
    print("Loading datasets...")
    meta_df = pd.read_csv(meta_path)
    market_df = pd.read_csv(market_path)
    
    # Filter to max_step
    market_df = market_df[market_df['step'] <= max_step]
    
    # Aggregate market orders per episode and player
    print("Aggregating market orders...")
    
    # Group by episode_id and player, count specific order types
    features = []
    
    for ep_id, group in market_df.groupby('episode_id'):
        ep_meta = meta_df[meta_df['episode_id'] == ep_id].iloc[0]
        p0_score = ep_meta['player_0_score']
        p1_score = ep_meta['player_1_score']
        
        for player in [0, 1]:
            p_group = group[group['player'] == player]
            opp_group = group[group['player'] == 1 - player]
            
            def get_counts(g):
                hires = len(g[g['order_type'] == 'HIRE'])
                melons = g[(g['order_type'] == 'BUY_SEED') & (g['item'] == 'MELON')]['quantity'].sum()
                strawberries = g[(g['order_type'] == 'BUY_SEED') & (g['item'] == 'STRAWBERRY')]['quantity'].sum()
                cows = g[(g['order_type'] == 'BUY_ANIMAL') & (g['item'] == 'COW')]['quantity'].sum()
                sheep = g[(g['order_type'] == 'BUY_ANIMAL') & (g['item'] == 'SHEEP')]['quantity'].sum()
                land = len(g[g['order_type'] == 'BUY_LAND'])
                return hires, melons, strawberries, cows, sheep, land
                
            p_hires, p_melons, p_strawberries, p_cows, p_sheep, p_land = get_counts(p_group)
            o_hires, o_melons, o_strawberries, o_cows, o_sheep, o_land = get_counts(opp_group)
            
            my_score = p0_score if player == 0 else p1_score
            opp_score = p1_score if player == 0 else p0_score
            margin = my_score - opp_score
            win = 1 if margin > 0 else 0
            
            features.append({
                'episode_id': ep_id,
                'player': player,
                'p_hires': p_hires,
                'p_melons': p_melons,
                'p_strawberries': p_strawberries,
                'p_cows': p_cows,
                'p_sheep': p_sheep,
                'p_land': p_land,
                'o_hires': o_hires,
                'o_melons': o_melons,
                'o_strawberries': o_strawberries,
                'o_cows': o_cows,
                'o_sheep': o_sheep,
                'o_land': o_land,
                'my_score': my_score,
                'opp_score': opp_score,
                'margin': margin,
                'win': win
            })
            
    df = pd.DataFrame(features)
    print(f"Extracted {len(df)} feature rows.")
    return df

if __name__ == "__main__":
    df = extract_features(
        'RESEARCH/kaggle_loop/training/datasets/matches_meta.csv',
        'RESEARCH/kaggle_loop/training/datasets/market_orders.csv',
        max_step=72
    )
    df.to_csv('RESEARCH/kaggle_loop/training/datasets/features_day3.csv', index=False)
    print("Saved features_day3.csv")
