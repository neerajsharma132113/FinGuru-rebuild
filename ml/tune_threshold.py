import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "transactions.csv")
df = pd.read_csv(path)

df["log_amount"] = np.log(df["amount"])
df["is_night"] = (df["hour"] < 6).astype(int)
FEATURES = ["log_amount", "is_night", "is_foreign", "txns_last_24h"]

# Same test set as before, then a validation set carved out of train
train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["is_fraud"])
train_part, valid = train_test_split(train, test_size=0.2, random_state=42, stratify=train["is_fraud"])

scaler = StandardScaler()
X_train = scaler.fit_transform(train_part[FEATURES])
X_valid = scaler.transform(valid[FEATURES])
X_test = scaler.transform(test[FEATURES])

model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, train_part["is_fraud"])

valid_scores = model.predict_proba(X_valid)[:, 1]
test_scores = model.predict_proba(X_test)[:, 1]

# Choose the threshold using VALIDATION data only
print("Validation fraud cases:", int(valid["is_fraud"].sum()), "of", len(valid))
best_threshold = 0.5
best_f1 = 0

for threshold in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    pred = (valid_scores >= threshold).astype(int)
    f1 = f1_score(valid["is_fraud"], pred, zero_division=0)
    print("threshold", threshold, "-> F1", round(f1, 3))
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

print("Chosen threshold:", best_threshold)


# Final check on the TEST set
def show(name, threshold):
    pred = (test_scores >= threshold).astype(int)
    print("\n" + name + " (threshold " + str(threshold) + ")")
    print("  flagged:  ", int(pred.sum()))
    print("  precision:", round(precision_score(test["is_fraud"], pred, zero_division=0), 3))
    print("  recall:   ", round(recall_score(test["is_fraud"], pred), 3))


show("Default", 0.5)
show("Tuned", best_threshold)