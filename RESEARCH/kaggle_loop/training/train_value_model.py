import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train_value_model():
    print("Loading datasets...")
    X_train = np.load("data/X_train.npy")
    y_train = np.load("data/y_train.npy")
    X_val = np.load("data/X_val.npy")
    y_val = np.load("data/y_val.npy")
    
    # Target index 0 is win probability
    y_train_win = y_train[:, 0]
    y_val_win = y_val[:, 0]
    
    print("Training Outcome/Value Model (RandomForest)...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train_win)
    
    print("Evaluating...")
    preds = clf.predict(X_val)
    print("Validation Accuracy (Win Prediction):", accuracy_score(y_val_win, preds))
    print(classification_report(y_val_win, preds, target_names=["LOSS", "WIN"]))
    
    os.makedirs("models", exist_ok=True)
    with open("models/value_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("Model saved to models/value_model.pkl")

if __name__ == "__main__":
    train_value_model()
