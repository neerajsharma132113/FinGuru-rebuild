import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, average_precision_score

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "transactions.csv")
df = pd.read_csv(path)

# Feature engineering
df["log_amount"] = np.log(df["amount"])
df["is_night"] = (df["hour"] < 6).astype(int)
FEATURES = ["log_amount", "is_night", "is_foreign", "txns_last_24h"]

# Same split as baseline.py
train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["is_fraud"])
X_train = train[FEATURES]
X_test = test[FEATURES]
y_train = train["is_fraud"]
y_test = test["is_fraud"]


def show(name, y_pred, scores=None):
    print("\n" + name)
    print("  flagged:  ", int(y_pred.sum()))
    print("  precision:", round(precision_score(y_test, y_pred, zero_division=0), 3))
    print("  recall:   ", round(recall_score(y_test, y_pred), 3))
    if scores is not None:
        print("  PR-AUC:   ", round(average_precision_score(y_test, scores), 3))


print("Test rows:", len(test), "| fraud in test:", int(y_test.sum()))

# Baseline: one rule
rule_pred = (test["amount"] > 3000).astype(int)
show("Baseline: flag amount > 3000", rule_pred, scores=test["amount"])

# Model 1: Logistic Regression (supervised)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # learn scaling from train only
X_test_scaled = scaler.transform(X_test)

logistic = LogisticRegression(max_iter=1000, class_weight="balanced")
logistic.fit(X_train_scaled, y_train)
show(
    "Logistic Regression",
    logistic.predict(X_test_scaled),
    scores=logistic.predict_proba(X_test_scaled)[:, 1],
)

# Model 2: Isolation Forest (unsupervised, never sees labels)
forest = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
forest.fit(X_train)
forest_pred = (forest.predict(X_test) == -1).astype(int)  # -1 means anomaly
show("Isolation Forest", forest_pred, scores=-forest.decision_function(X_test))