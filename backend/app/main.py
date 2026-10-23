from fastapi import FastAPI, Query
from app.services.finance import calculate_emi, calculate_schedule, calculate_affordability

app = FastAPI(title="FinGuru")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/emi")
def emi(
    principal: float = Query(gt=0),
    annual_rate_percent: float = Query(ge=0),
    tenure_months: int = Query(gt=0),
):
    return calculate_emi(principal, annual_rate_percent, tenure_months)

@app.get("/schedule")
def schedule(
    principal: float = Query(gt=0),
    annual_rate_percent: float = Query(ge=0),
    tenure_months: int = Query(gt=0, le=600),
):
    return calculate_schedule(principal, annual_rate_percent, tenure_months)

@app.get("/affordability")
def affordability(
    monthly_income: float = Query(gt=0),
    existing_emi: float = Query(ge=0),
    annual_rate_percent: float = Query(ge=0),
    tenure_months: int = Query(gt=0, le=600),
):
    return calculate_affordability(monthly_income, existing_emi, annual_rate_percent, tenure_months)