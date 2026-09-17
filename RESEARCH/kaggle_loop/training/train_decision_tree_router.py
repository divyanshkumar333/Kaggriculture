import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
import os

def train_and_export_tree():
    df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/features_day3.csv')
    
    # We want to predict if playing Dumper (Melon Frontrunner) or Maximizer (v057) is better.
    # We don't have that exact label. But we DO know that if the opponent plays Melons (o_melons > 0),
    # then our best strategy is to Dump (v060).
    # Since we know this, we can just use the tree to learn the `o_melons > 0` rule from the data!
    # Let's create a synthetic label "should_dump" based on `win` and `o_melons`.
    # Wait, instead of synthetic labels, I will just use the XGBoost value model to label the best action!
    
    # Actually, the user wants to convert learned structure into a lightweight agent.
    # Let's just train a Decision Tree on the dataset directly to predict P(WIN) and extract the rules!
    
    # Features
    features = ['p_hires', 'p_melons', 'p_strawberries', 'p_cows', 'p_sheep', 'p_land',
                'o_hires', 'o_melons', 'o_strawberries', 'o_cows', 'o_sheep', 'o_land']
                
    X = df[features]
    y = df['win']
    
    # Train Decision Tree
    clf = DecisionTreeClassifier(max_depth=2, random_state=42)
    clf.fit(X, y)
    
    # Export rules
    tree_rules = export_text(clf, feature_names=features)
    print("Decision Tree Rules (Predicting P(WIN)):")
    print(tree_rules)
    
    # Since the tree predicts win, we can see which leaf has the highest win probability.
    # If o_melons > 0 leads to low win probability (because they are dumping),
    # that means we should switch strategy.
    
if __name__ == "__main__":
    train_and_export_tree()
