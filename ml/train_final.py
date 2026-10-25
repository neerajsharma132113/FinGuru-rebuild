import os
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ml_folder = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(ml_folder, "data", "transactions.csv"))

df["log_amount"] = np.log(df["amount"])
df["is_night"] = (df["hour"] < 6).astype(int)
FEATURES = ["log_amount", "is_night", "is_foreign", "txns_last_24h"]

# Same splits as tune_threshold.py, so the results match
train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["is_fraud"])
train_part, valid = train_test_split(train, test_size=0.2, random_state=42, stratify=train["is_fraud"])

scaler = StandardScaler()
X_train = scaler.fit_transform(train_part[FEATURES])
X_valid = scaler.transform(valid[FEATURES])

model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, train_part["is_fraud"])

# Choose the threshold on validation data
valid_scores = model.predict_proba(X_valid)[:, 1]
best_threshold = 0.5
best_f1 = 0
for threshold in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    pred = (valid_scores >= threshold).astype(int)
    f1 = f1_score(valid["is_fraud"], pred, zero_division=0)
    if f1 > best_f1:
        best_f1 = f1
        best_threshold = threshold

# Save everything the backend will need in ONE file
artifact = {
    "model": model,
    "scaler": scaler,
    "features": FEATURES,
    "threshold": best_threshold,
    "note": "Trained on synthetic data. Not validated on real fraud.",
}
model_folder = os.path.join(ml_folder, "..", "backend", "models")
os.makedirs(model_folder, exist_ok=True)
model_path = os.path.join(model_folder, "fraud_model.joblib")
joblib.dump(artifact, model_path)
print("Saved model. Threshold:", best_threshold)

# Check: load it back and score two examples
loaded = joblib.load(model_path)


def score(amount, hour, is_foreign, txns_last_24h):
    row = pd.DataFrame([{
        "log_amount": np.log(amount),
        "is_night": int(hour < 6),
        "is_foreign": is_foreign,
        "txns_last_24h": txns_last_24h,
    }])
    scaled = loaded["scaler"].transform(row[loaded["features"]])
    return loaded["model"].predict_proba(scaled)[0, 1]


normal_score = score(450, 14, 0, 2)
risky_score = score(9000, 2, 1, 8)
print("Normal example  -> fraud score:", round(normal_score, 3))
print("Risky example   -> fraud score:", round(risky_score, 3))