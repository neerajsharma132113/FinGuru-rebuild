from app.services.finance import calculate_emi

print(calculate_emi(500000, 10, 60))
print(calculate_emi(500000, 0, 60))

try:
    calculate_emi(-1000, 10, 60)
except ValueError as error:
    print("Caught error:", error)