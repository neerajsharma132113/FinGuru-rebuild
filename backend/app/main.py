import datetime
from typing import Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from app.services.finance import calculate_emi, calculate_schedule, calculate_affordability, summarize_by_month
from app.database import init_db, add_transaction, list_transactions
app = FastAPI(title="FinGuru")
init_db()


class NewTransaction(BaseModel):
    date: datetime.date
    category: str = Field(min_length=1, max_length=50)
    kind: Literal["income", "expense"]
    amount: float = Field(gt=0, le=100000000)

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

@app.post("/transactions", status_code=201)
def create_transaction(transaction: NewTransaction):
    add_transaction(str(transaction.date), transaction.category, transaction.kind, transaction.amount)
    return {"message": "Transaction added"}


@app.get("/transactions")
def get_transactions():
    return list_transactions()

@app.get("/summary")
def summary():
    return summarize_by_month(list_transactions())