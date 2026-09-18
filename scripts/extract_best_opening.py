import pandas as pd

# Load Meta
meta = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/matches_meta.csv', encoding='utf-8', encoding_errors='ignore')

# Get top 10 scores
top_scores = []
for _, row in meta.iterrows():
    top_scores.append({'ep': row['episode_id'], 'player': 0, 'score': row['player_0_score'], 'win': row['winner'] == 'Player 0'})
    top_scores.append({'ep': row['episode_id'], 'player': 1, 'score': row['player_1_score'], 'win': row['winner'] == 'Player 1'})

scores_df = pd.DataFrame(top_scores)
scores_df = scores_df.sort_values(by='score', ascending=False)
top_eps = scores_df.head(10)

# Load Actions
actions = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/farmer_actions.csv')

# Get top episodes that actually exist in actions
available_eps = set(actions['episode_id'].unique())
top_eps = top_eps[top_eps['ep'].isin(available_eps)]

print("\nExtracting opening sequence for the #1 highest scoring player in actions data...")
best_ep = top_eps.iloc[0]['ep']
best_p = top_eps.iloc[0]['player']

best_actions = actions[(actions['episode_id'] == best_ep) & (actions['player'] == best_p)].copy()
best_actions = best_actions.sort_values(by='step')

print("\nFirst 40 Steps of the Best Player:")
print(best_actions.head(40)[['step', 'action_verb', 'target_or_item', 'quantity_or_coord']])

