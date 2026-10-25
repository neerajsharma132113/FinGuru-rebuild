import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # fixed seed = same data every run

N_NORMAL = 9800
N_FRAUD = 200
CATEGORIES = ["grocery", "food", "fuel", "shopping", "travel", "bills", "entertainment"]


def make_normal(n):
    return pd.DataFrame({
        "amount": rng.lognormal(mean=6.5, sigma=0.8, size=n).round(2),
        "hour": rng.integers(6, 23, size=n),
        "category": rng.choice(CATEGORIES, size=n),
        "is_foreign": (rng.random(n) < 0.03).astype(int),
        "txns_last_24h": rng.poisson(2, size=n),
        "is_fraud": 0,
    })


def make_fraud(n):
    night = rng.random(n) < 0.6  # 60% of fraud happens at night
    hours = np.where(night, rng.integers(0, 6, size=n), rng.integers(6, 23, size=n))
    return pd.DataFrame({
        "amount": rng.lognormal(mean=7.8, sigma=1.0, size=n).round(2),
        "hour": hours,
        "category": rng.choice(CATEGORIES, size=n),
        "is_foreign": (rng.random(n) < 0.4).astype(int),
        "txns_last_24h": rng.poisson(6, size=n),
        "is_fraud": 1,
    })


normal = make_normal(N_NORMAL)
fraud = make_fraud(N_FRAUD)

df = pd.concat([normal, fraud])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle rows
df.insert(0, "transaction_id", range(1, len(df) + 1))

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_folder, exist_ok=True)
df.to_csv(os.path.join(data_folder, "transactions.csv"), index=False)

print("Shape:", df.shape)
print("Fraud count:", df["is_fraud"].sum(), "(", round(df["is_fraud"].mean() * 100, 2), "% )")
print(df.head())
print(df.groupby("is_fraud")[["amount", "hour", "is_foreign", "txns_last_24h"]].mean().round(2))