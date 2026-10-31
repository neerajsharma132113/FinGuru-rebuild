from fastmcp import FastMCP
from app.services.finance import calculate_emi

mcp = FastMCP("FinGuru")


@mcp.tool
def emi_calculator(principal: float, annual_rate_percent: float, tenure_months: int) -> dict:
    """Calculate the monthly EMI, total interest and total payment for a loan.
    principal is in rupees, annual_rate_percent is the yearly interest rate
    (for example 10 for 10 percent), tenure_months is 1 to 600."""
    if tenure_months > 600:
        raise ValueError("Tenure cannot be more than 600 months")
    return calculate_emi(principal, annual_rate_percent, tenure_months)


if __name__ == "__main__":
    mcp.run()  # default transport is stdio