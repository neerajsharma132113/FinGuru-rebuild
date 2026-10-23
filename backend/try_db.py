from app.database import init_db, add_transaction, list_transactions

init_db()
add_transaction("2026-10-01", "salary", "income", 80000)
add_transaction("2026-10-03", "groceries", "expense", 2450.50)

for t in list_transactions():
    print(t)

try:
    add_transaction("2026-10-04", "food", "expense", -5)
except ValueError as error:
    print("Caught error:", error)