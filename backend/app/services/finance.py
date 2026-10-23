def calculate_emi(principal, annual_rate_percent, tenure_months):
    # 1. Validate inputs
    if principal <= 0:
        raise ValueError("Principal must be greater than 0")
    if annual_rate_percent < 0:
        raise ValueError("Interest rate cannot be negative")
    if tenure_months <= 0:
        raise ValueError("Tenure must be greater than 0")

    # 2. Monthly interest rate
    monthly_rate = annual_rate_percent / 12 / 100

    # 3. EMI calculation
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        growth = (1 + monthly_rate) ** tenure_months
        emi = principal * monthly_rate * growth / (growth - 1)

    # 4. Totals
    total_payment = emi * tenure_months
    total_interest = total_payment - principal

    return {
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
    }

def calculate_schedule(principal, annual_rate_percent, tenure_months):
    # Reuse our existing function (it also validates the inputs)
    emi = calculate_emi(principal, annual_rate_percent, tenure_months)["emi"]
    monthly_rate = annual_rate_percent / 12 / 100

    schedule = []
    balance = principal

    for month in range(1, tenure_months + 1):
        interest = round(balance * monthly_rate, 2)

        if month == tenure_months:
            # Last month: clear the remaining balance
            principal_paid = round(balance, 2)
            payment = round(principal_paid + interest, 2)
        else:
            principal_paid = round(emi - interest, 2)
            payment = emi

        balance = round(balance - principal_paid, 2)

        schedule.append({
            "month": month,
            "payment": payment,
            "interest": interest,
            "principal_paid": principal_paid,
            "balance": balance,
        })

    return schedule