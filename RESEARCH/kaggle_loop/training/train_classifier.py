import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train_classifier():
    print("Loading datasets...")
    X_train = np.load("data/X_train.npy")
    y_train = np.load("data/y_train.npy")
    X_val = np.load("data/X_val.npy")
    y_val = np.load("data/y_val.npy")
    
    # Target index 1 is opponent archetype
    y_train_arch = y_train[:, 1]
    y_val_arch = y_val[:, 1]
    
    print("Training Opponent Archetype Classifier (RandomForest)...")
    clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    clf.fit(X_train, y_train_arch)
    
    print("Evaluating...")
    preds = clf.predict(X_val)
    print(classification_report(y_val_arch, preds, zero_division=0))
    
    os.makedirs("models", exist_ok=True)
    with open("models/opponent_classifier.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("Model saved to models/opponent_classifier.pkl")

if __name__ == "__main__":
    train_classifier()
