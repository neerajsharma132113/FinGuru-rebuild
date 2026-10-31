from fastmcp import FastMCP
from app.services.finance import calculate_emi, next_best_action, compare_loans

mcp = FastMCP("FinGuru")


@mcp.tool
def emi_calculator(principal: float, annual_rate_percent: float, tenure_months: int) -> dict:
    """Calculate the monthly EMI, total interest and total payment for a loan.
    principal is in rupees, annual_rate_percent is the yearly interest rate
    (for example 10 for 10 percent), tenure_months is 1 to 600."""
    if tenure_months > 600:
        raise ValueError("Tenure cannot be more than 600 months")
    return calculate_emi(principal, annual_rate_percent, tenure_months)


@mcp.tool
def suggest_next_action(
    monthly_income: float,
    monthly_expenses: float,
    monthly_emi: float,
    emergency_fund: float,
) -> dict:
    """Suggest one next step (HELP, WARN, SAVE or NO ACTION) using fixed, readable rules.
    All amounts are in rupees per month, except emergency_fund which is the total saved.
    monthly_expenses means all spending, EMI included. The result includes the reason.
    This is a simple educational rule check, not financial advice."""
    return next_best_action(monthly_income, monthly_expenses, monthly_emi, emergency_fund)


@mcp.tool
def compare_two_loans(
    principal: float,
    annual_rate_percent_a: float,
    tenure_months_a: int,
    annual_rate_percent_b: float,
    tenure_months_b: int,
) -> dict:
    """Compare two loans of the same amount (principal in rupees) that differ in
    interest rate and tenure. Returns EMI, total interest and total payment for each,
    the differences (loan B minus loan A) and which loan has the lower total cost."""
    if tenure_months_a > 600 or tenure_months_b > 600:
        raise ValueError("Tenure cannot be more than 600 months")
    return compare_loans(
        principal, annual_rate_percent_a, tenure_months_a, annual_rate_percent_b, tenure_months_b
    )


if __name__ == "__main__":
    mcp.run()  # default transport is stdio