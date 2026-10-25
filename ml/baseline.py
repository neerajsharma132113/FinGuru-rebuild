import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "transactions.csv")
df = pd.read_csv(path)

train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["is_fraud"])

y_true = test["is_fraud"]
print("Test rows:", len(test), "| fraud in test:", y_true.sum())


def show(name, y_pred):
    print("\n" + name)
    print("  flagged:  ", y_pred.sum())
    print("  accuracy: ", round(accuracy_score(y_true, y_pred), 4))
    print("  precision:", round(precision_score(y_true, y_pred, zero_division=0), 4))
    print("  recall:   ", round(recall_score(y_true, y_pred), 4))


# Baseline 1: never predict fraud
never_fraud = pd.Series(0, index=test.index)
show("Baseline 1: never fraud", never_fraud)

# Baseline 2: one simple rule
big_amount = (test["amount"] > 3000).astype(int)
show("Baseline 2: flag amount > 3000", big_amount)