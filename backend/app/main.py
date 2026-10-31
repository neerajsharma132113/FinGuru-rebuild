import datetime
from typing import Literal

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.services.finance import (
    calculate_emi,
    calculate_schedule,
    calculate_affordability,
    summarize_by_month,
    simulate_income_change,
    simulate_loan,
    next_best_action,
    health_check,
)
from app.database import (
    init_db,
    add_transaction,
    list_transactions,
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.security import (
    hash_password,
    check_password,
    create_access_token,
    read_access_token,
    is_locked,
    record_failure,
    clear_failures,
)
from app.fraud import score_transaction
from app.rag import load_chunks, search_chunks

app = FastAPI(title="FinGuru")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

init_db()

MAX_MONEY = 100000000
MAX_RATE = 100


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


# ---------- Public calculators ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/emi")
def emi(
    principal: float = Query(gt=0, le=MAX_MONEY),
    annual_rate_percent: float = Query(ge=0, le=MAX_RATE),
    tenure_months: int = Query(gt=0, le=600),
):
    return calculate_emi(principal, annual_rate_percent, tenure_months)


@app.get("/schedule")
def schedule(
    principal: float = Query(gt=0, le=MAX_MONEY),
    annual_rate_percent: float = Query(ge=0, le=MAX_RATE),
    tenure_months: int = Query(gt=0, le=600),
):
    return calculate_schedule(principal, annual_rate_percent, tenure_months)


@app.get("/affordability")
def affordability(
    monthly_income: float = Query(gt=0, le=MAX_MONEY),
    existing_emi: float = Query(ge=0, le=MAX_MONEY),
    annual_rate_percent: float = Query(ge=0, le=MAX_RATE),
    tenure_months: int = Query(gt=0, le=600),
):
    return calculate_affordability(monthly_income, existing_emi, annual_rate_percent, tenure_months)


@app.get("/simulate/income-change")
def income_change(
    monthly_income: float = Query(gt=0, le=MAX_MONEY),
    monthly_expenses: float = Query(ge=0, le=MAX_MONEY),
    income_change_percent: float = Query(ge=-100, le=1000),
):
    return simulate_income_change(monthly_income, monthly_expenses, income_change_percent)


@app.get("/simulate/loan")
def loan_scenario(
    monthly_income: float = Query(gt=0, le=MAX_MONEY),
    monthly_expenses: float = Query(ge=0, le=MAX_MONEY),
    loan_amount: float = Query(gt=0, le=MAX_MONEY),
    annual_rate_percent: float = Query(ge=0, le=MAX_RATE),
    tenure_months: int = Query(gt=0, le=600),
):
    return simulate_loan(monthly_income, monthly_expenses, loan_amount, annual_rate_percent, tenure_months)


@app.get("/next-best-action")
def get_next_best_action(
    monthly_income: float = Query(gt=0, le=MAX_MONEY),
    monthly_expenses: float = Query(ge=0, le=MAX_MONEY),
    monthly_emi: float = Query(ge=0, le=MAX_MONEY),
    emergency_fund: float = Query(ge=0, le=MAX_MONEY),
):
    return next_best_action(monthly_income, monthly_expenses, monthly_emi, emergency_fund)


# ---------- Accounts ----------

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
    if is_locked(data.email):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")

    user = get_user_by_email(data.email)
    if user is None or not check_password(data.password, user["password_hash"]):
        record_failure(data.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    clear_failures(data.email)
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


# ---------- Private data (login required) ----------

@app.post("/transactions", status_code=201)
def create_transaction(transaction: NewTransaction, current_user: dict = Depends(get_current_user)):
    add_transaction(
        current_user["id"],
        str(transaction.date),
        transaction.category,
        transaction.kind,
        transaction.amount,
    )
    return {"message": "Transaction added"}


@app.get("/transactions")
def get_transactions(current_user: dict = Depends(get_current_user)):
    return list_transactions(current_user["id"])


@app.get("/summary")
def summary(current_user: dict = Depends(get_current_user)):
    return summarize_by_month(list_transactions(current_user["id"]))


@app.get("/health-check")
def get_health_check(
    monthly_emi: float = Query(ge=0, le=MAX_MONEY),
    emergency_fund: float = Query(ge=0, le=MAX_MONEY),
    current_user: dict = Depends(get_current_user),
):
    transactions = list_transactions(current_user["id"])
    return health_check(transactions, monthly_emi, emergency_fund)


# ---------- Fraud model ----------

@app.get("/fraud-score")
def fraud_score(
    amount: float = Query(gt=0, le=100000000),
    hour: int = Query(ge=0, le=23),
    is_foreign: int = Query(ge=0, le=1),
    txns_last_24h: int = Query(ge=0, le=1000),
    current_user: dict = Depends(get_current_user),
):
    try:
        return score_transaction(amount, hour, is_foreign, txns_last_24h)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Fraud model not available")


# ---------- Knowledge notes (retrieval only) ----------

knowledge_chunks = load_chunks()  # loaded once, when the app starts


@app.get("/ask")
def ask(
    question: str = Query(min_length=3, max_length=300),
    current_user: dict = Depends(get_current_user),
):
    results = search_chunks(question, knowledge_chunks, top_k=3, min_score=0.1, min_coverage=0.5)

    if len(results) == 0:
        return {
            "found": False,
            "message": "I could not find this in the FinGuru knowledge notes, so I won't guess.",
            "sources": [],
        }

    return {
        "found": True,
        "message": "Passages from the knowledge notes (general education, not personal advice):",
        "sources": results,
    }