import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, log_loss
import pickle

def train_xgb():
    print("Loading features...")
    df = pd.read_csv('RESEARCH/kaggle_loop/training/datasets/features_day3.csv')
    
    # We will predict P(WIN) from our features (p_*) and opponent features (o_*)
    features = ['p_hires', 'p_melons', 'p_strawberries', 'p_cows', 'p_sheep', 'p_land',
                'o_hires', 'o_melons', 'o_strawberries', 'o_cows', 'o_sheep', 'o_land']
                
    X = df[features]
    y = df['win']
    
    # We will use Stratified K-Fold to evaluate
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    accs = []
    loglosses = []
    
    best_model = None
    best_acc = 0
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # Train XGBoost
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            objective='binary:logistic',
            random_state=42,
            eval_metric='logloss'
        )
        
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        ll = log_loss(y_test, y_prob)
        
        accs.append(acc)
        loglosses.append(ll)
        
        if acc > best_acc:
            best_acc = acc
            best_model = model
            
    print(f"Mean Accuracy: {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
    print(f"Mean LogLoss:  {np.mean(loglosses):.4f} +/- {np.std(loglosses):.4f}")
    
    # Feature Importance
    importances = best_model.feature_importances_
    feat_imp = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
    print("\nFeature Importances:")
    for f, imp in feat_imp:
        print(f"  {f:15s}: {imp:.4f}")
        
    # Retrain on full dataset
    print("\nRetraining on full dataset...")
    final_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        objective='binary:logistic',
        random_state=42
    )
    final_model.fit(X, y)
    
    # Save model
    with open('RESEARCH/kaggle_loop/training/models/xgb_value_model.pkl', 'wb') as f:
        pickle.dump(final_model, f)
    print("Saved to RESEARCH/kaggle_loop/training/models/xgb_value_model.pkl")

if __name__ == "__main__":
    import os
    os.makedirs('RESEARCH/kaggle_loop/training/models', exist_ok=True)
    train_xgb()
