import os
import numpy as np
import pandas as pd
import joblib

BACKEND_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BACKEND_FOLDER, "models", "fraud_model.joblib")

# Load once, when the app starts. None means the file is missing.
artifact = None
if os.path.exists(MODEL_PATH):
    artifact = joblib.load(MODEL_PATH)

REASON_TEXT = {
    "log_amount": "Amount is large compared to typical transactions",
    "is_night": "Made at night (12am to 6am)",
    "is_foreign": "Foreign transaction",
    "txns_last_24h": "Many transactions in the last 24 hours",
}


def score_transaction(amount, hour, is_foreign, txns_last_24h):
    if artifact is None:
        raise RuntimeError("Fraud model file not found")

    # Build the features exactly as in training
    row = pd.DataFrame([{
        "log_amount": np.log(amount),
        "is_night": int(hour < 6),
        "is_foreign": is_foreign,
        "txns_last_24h": txns_last_24h,
    }])
    scaled = artifact["scaler"].transform(row[artifact["features"]])

    score = float(artifact["model"].predict_proba(scaled)[0, 1])
    flagged = bool(score >= artifact["threshold"])

    # Reasons: features pushing the score toward fraud
    pushes = artifact["model"].coef_[0] * scaled[0]
    pairs = list(zip(artifact["features"], pushes))
    pairs.sort(key=lambda pair: pair[1], reverse=True)

    reasons = []
    for name, push in pairs:
        if push > 0 and len(reasons) < 3:
            reasons.append(REASON_TEXT[name])

    return {
        "fraud_score": round(score, 4),
        "flagged": flagged,
        "threshold": float(artifact["threshold"]),
        "reasons": reasons,
        "note": artifact["note"],
    }