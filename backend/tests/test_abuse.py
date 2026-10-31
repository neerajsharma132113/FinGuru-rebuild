import base64
import json
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import database, security

client = TestClient(app)
# This client returns a 500 response instead of re-raising the crash,
# so we can see crashes as status codes.
safe_client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "test.db"))
    monkeypatch.setattr(security, "SECRET_KEY", "test-secret-key-for-tests-only-0123456789")
    security.failed_logins.clear()
    database.init_db()


def make_headers(email="asha@example.com"):
    client.post("/register", json={"email": email, "password": "MySecret123"})
    login = client.post("/login", json={"email": email, "password": "MySecret123"})
    return {"Authorization": "Bearer " + login.json()["access_token"]}


def b64(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


# ---------- SQL injection ----------

def test_sql_injection_in_login_email():
    response = client.post("/login", json={"email": "' OR '1'='1", "password": "x"})
    assert response.status_code == 401


def test_sql_text_in_category_is_stored_as_plain_text():
    headers = make_headers()
    evil = "x'); DROP TABLE transactions;--"
    body = {"date": "2026-10-01", "category": evil, "kind": "expense", "amount": 100}
    assert client.post("/transactions", json=body, headers=headers).status_code == 201

    rows = client.get("/transactions", headers=headers).json()
    assert len(rows) == 1
    assert rows[0]["category"] == evil

    # the table still works afterwards
    assert client.post("/transactions", json=body, headers=headers).status_code == 201


# ---------- Oversized input ----------

def test_oversized_fields_are_rejected():
    headers = make_headers()
    long_category = {"date": "2026-10-01", "category": "a" * 51, "kind": "expense", "amount": 100}
    assert client.post("/transactions", json=long_category, headers=headers).status_code == 422

    long_email = "a" * 95 + "@example.com"
    assert client.post("/register", json={"email": long_email, "password": "MySecret123"}).status_code == 422

    long_password = "a" * 129
    assert client.post("/register", json={"email": "b@example.com", "password": long_password}).status_code == 422


# ---------- Forged tokens ----------

def test_token_signed_with_wrong_key_is_rejected():
    forged = jwt.encode(
        {"sub": "1", "exp": int(time.time()) + 3600},
        "a-completely-different-secret-key-0123456789",
        algorithm="HS256",
    )
    response = client.get("/me", headers={"Authorization": "Bearer " + forged})
    assert response.status_code == 401


def test_unsigned_alg_none_token_is_rejected():
    token = b64({"alg": "none", "typ": "JWT"}) + "." + b64({"sub": "1"}) + "."
    response = client.get("/me", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 401


def test_valid_token_for_missing_user_is_rejected():
    token = security.create_access_token(9999)
    response = client.get("/me", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 401


def test_wrong_auth_scheme_is_rejected():
    response = client.get("/me", headers={"Authorization": "Basic abc123"})
    assert response.status_code == 401


# ---------- Odd questions to /ask ----------

def test_ask_question_too_long():
    headers = make_headers()
    response = client.get("/ask", params={"question": "a" * 301}, headers=headers)
    assert response.status_code == 422


def test_ask_with_html_does_not_crash():
    headers = make_headers()
    response = client.get("/ask", params={"question": "<script>alert(1)</script>"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["found"] is False


# ---------- Extreme numbers on public endpoints ----------

BAD_NUMBERS = [
    ("/emi", {"principal": "inf", "annual_rate_percent": 10, "tenure_months": 60}),
    ("/emi", {"principal": "nan", "annual_rate_percent": 10, "tenure_months": 60}),
    ("/emi", {"principal": "1e308", "annual_rate_percent": 10, "tenure_months": 60}),
    ("/emi", {"principal": 500000, "annual_rate_percent": "inf", "tenure_months": 60}),
    ("/emi", {"principal": 500000, "annual_rate_percent": 1000000, "tenure_months": 600}),
    ("/schedule", {"principal": "inf", "annual_rate_percent": 10, "tenure_months": 12}),
    ("/affordability", {"monthly_income": "inf", "existing_emi": 0, "annual_rate_percent": 10, "tenure_months": 60}),
    ("/simulate/income-change", {"monthly_income": "inf", "monthly_expenses": 40000, "income_change_percent": -20}),
    ("/simulate/loan", {"monthly_income": 80000, "monthly_expenses": 40000, "loan_amount": "inf", "annual_rate_percent": 10, "tenure_months": 60}),
    ("/next-best-action", {"monthly_income": "inf", "monthly_expenses": 40000, "monthly_emi": 10000, "emergency_fund": 60000}),
]


@pytest.mark.parametrize("path, params", BAD_NUMBERS)
def test_extreme_numbers_are_rejected_not_crashed(path, params):
    response = safe_client.get(path, params=params)
    assert response.status_code == 422