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

def calculate_affordability(monthly_income, existing_emi, annual_rate_percent, tenure_months, max_emi_ratio=0.40):
    # 1. Validate inputs
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0")
    if existing_emi < 0:
        raise ValueError("Existing EMI cannot be negative")
    if annual_rate_percent < 0:
        raise ValueError("Interest rate cannot be negative")
    if tenure_months <= 0:
        raise ValueError("Tenure must be greater than 0")

    # 2. How much EMI can we still afford?
    max_emi = monthly_income * max_emi_ratio - existing_emi
    if max_emi <= 0:
        return {"max_emi": 0, "max_loan_amount": 0}

    # 3. Convert that EMI into a loan amount
    monthly_rate = annual_rate_percent / 12 / 100
    if monthly_rate == 0:
        max_loan = max_emi * tenure_months
    else:
        growth = (1 + monthly_rate) ** tenure_months
        max_loan = max_emi * (growth - 1) / (monthly_rate * growth)

    return {
        "max_emi": round(max_emi, 2),
        "max_loan_amount": round(max_loan, 2),
    }


def summarize_by_month(transactions):
    months = {}

    for t in transactions:
        month = t["date"][:7]
        if month not in months:
            months[month] = {"income": 0, "expenses": 0}

        if t["kind"] == "income":
            months[month]["income"] += t["amount"]
        else:
            months[month]["expenses"] += t["amount"]

    result = []
    for month in sorted(months):
        income = round(months[month]["income"], 2)
        expenses = round(months[month]["expenses"], 2)
        savings = round(income - expenses, 2)

        if income > 0:
            savings_rate = round(savings / income * 100, 2)
        else:
            savings_rate = None  # cannot divide by zero income

        result.append({
            "month": month,
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "savings_rate_percent": savings_rate,
        })

    return result

def simulate_income_change(monthly_income, monthly_expenses, income_change_percent):
    # 1. Validate inputs
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than 0")
    if monthly_expenses < 0:
        raise ValueError("Monthly expenses cannot be negative")
    if income_change_percent < -100 or income_change_percent > 1000:
        raise ValueError("Income change must be between -100 and 1000 percent")

    # 2. New income after the change
    new_income = monthly_income * (1 + income_change_percent / 100)

    # 3. Savings before and after
    savings_before = monthly_income - monthly_expenses
    savings_after = new_income - monthly_expenses

    rate_before = round(savings_before / monthly_income * 100, 2)
    if new_income > 0:
        rate_after = round(savings_after / new_income * 100, 2)
    else:
        rate_after = None  # no income, so a rate makes no sense

    return {
        "before": {
            "income": round(monthly_income, 2),
            "savings": round(savings_before, 2),
            "savings_rate_percent": rate_before,
        },
        "after": {
            "income": round(new_income, 2),
            "savings": round(savings_after, 2),
            "savings_rate_percent": rate_after,
        },
    }