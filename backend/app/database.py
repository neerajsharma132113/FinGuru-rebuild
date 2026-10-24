import sqlite3

from app.config import DB_FILE


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            kind TEXT NOT NULL,
            amount_paise INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_transaction(date, category, kind, amount):
    if kind not in ("income", "expense"):
        raise ValueError("kind must be 'income' or 'expense'")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    conn = get_connection()
    conn.execute(
        "INSERT INTO transactions (date, category, kind, amount_paise) VALUES (?, ?, ?, ?)",
        (date, category, kind, round(amount * 100)),
    )
    conn.commit()
    conn.close()


def list_transactions():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, date, category, kind, amount_paise FROM transactions ORDER BY id"
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "date": row["date"],
            "category": row["category"],
            "kind": row["kind"],
            "amount": row["amount_paise"] / 100,
        })
    return result