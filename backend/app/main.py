import datetime
from typing import Literal

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from app.services.finance import calculate_emi, calculate_schedule, calculate_affordability, summarize_by_month, simulate_income_change, simulate_loan, next_best_action
from app.database import init_db, add_transaction, list_transactions, create_user, get_user_by_email, get_user_by_id
from app.security import hash_password, check_password, create_access_token, read_access_token

app = FastAPI(title="FinGuru")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
init_db()


class NewTransaction(BaseModel):
    date: datetime.date
    category: str = Field(min_length=1, max_length=50)
    kind: Literal["income", "expense"]
    amount: float = Field(gt=0, le=100000000)


class NewUser(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginData(BaseModel):
    email: str = Field(max_length=100)
    password: str = Field(max_length=128)


bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    user_id = read_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


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
def create_transaction(transaction: NewTransaction, current_user: dict = Depends(get_current_user)):
    add_transaction(current_user["id"], str(transaction.date), transaction.category, transaction.kind, transaction.amount)
    return {"message": "Transaction added"}


@app.get("/transactions")
def get_transactions(current_user: dict = Depends(get_current_user)):
    return list_transactions(current_user["id"])


@app.get("/summary")
def summary(current_user: dict = Depends(get_current_user)):
    return summarize_by_month(list_transactions(current_user["id"]))


@app.post("/register", status_code=201)
def register(user: NewUser):
    password_hash = hash_password(user.password)
    try:
        create_user(user.email, password_hash)
    except ValueError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"message": "User registered"}


@app.post("/login")
def login(data: LoginData):
    user = get_user_by_email(data.email)
    if user is None or not check_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/simulate/income-change")
def income_change(
    monthly_income: float = Query(gt=0),
    monthly_expenses: float = Query(ge=0),
    income_change_percent: float = Query(ge=-100, le=1000),
):
    return simulate_income_change(monthly_income, monthly_expenses, income_change_percent)

@app.get("/simulate/loan")
def loan_scenario(
    monthly_income: float = Query(gt=0),
    monthly_expenses: float = Query(ge=0),
    loan_amount: float = Query(gt=0),
    annual_rate_percent: float = Query(ge=0),
    tenure_months: int = Query(gt=0, le=600),
):
    return simulate_loan(monthly_income, monthly_expenses, loan_amount, annual_rate_percent, tenure_months)

@app.get("/next-best-action")
def get_next_best_action(
    monthly_income: float = Query(gt=0),
    monthly_expenses: float = Query(ge=0),
    monthly_emi: float = Query(ge=0),
    emergency_fund: float = Query(ge=0),
):
    return next_best_action(monthly_income, monthly_expenses, monthly_emi, emergency_fund)