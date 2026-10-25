from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)
from app import database, security, fraud


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "test.db"))
    monkeypatch.setattr(security, "SECRET_KEY", "test-secret-key-for-tests-only-0123456789")
    database.init_db()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_emi_ok():
    response = client.get(
        "/emi",
        params={"principal": 500000, "annual_rate_percent": 10, "tenure_months": 60},
    )
    assert response.status_code == 200
    assert response.json()["emi"] == 10623.52


def test_emi_bad_input():
    response = client.get(
        "/emi",
        params={"principal": -5, "annual_rate_percent": 10, "tenure_months": 60},
    )
    assert response.status_code == 422


def test_schedule_too_long():
    response = client.get(
        "/schedule",
        params={"principal": 500000, "annual_rate_percent": 10, "tenure_months": 601},
    )
    assert response.status_code == 422

def test_affordability_ok():
    response = client.get(
        "/affordability",
        params={
            "monthly_income": 80000,
            "existing_emi": 10000,
            "annual_rate_percent": 10,
            "tenure_months": 60,
        },
    )
    assert response.status_code == 200
    assert response.json()["max_emi"] == 22000


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    security.failed_logins.clear()
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "test.db"))
    database.init_db()



def test_register_ok_and_password_not_stored():
    response = client.post("/register", json={"email": "Asha@Example.com", "password": "MySecret123"})
    assert response.status_code == 201

    user = database.get_user_by_email("asha@example.com")
    assert user is not None
    assert user["password_hash"] != "MySecret123"
    assert user["password_hash"].startswith("$argon2")


def test_register_duplicate_email():
    body = {"email": "asha@example.com", "password": "MySecret123"}
    client.post("/register", json=body)
    response = client.post("/register", json=body)
    assert response.status_code == 409


def test_register_short_password():
    response = client.post("/register", json={"email": "asha@example.com", "password": "abc"})
    assert response.status_code == 422


def test_register_bad_email():
    response = client.post("/register", json={"email": "not-an-email", "password": "MySecret123"})
    assert response.status_code == 422

def test_login_ok():
    client.post("/register", json={"email": "asha@example.com", "password": "MySecret123"})
    response = client.post("/login", json={"email": "asha@example.com", "password": "MySecret123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert security.read_access_token(token) is not None


def test_login_wrong_password():
    client.post("/register", json={"email": "asha@example.com", "password": "MySecret123"})
    response = client.post("/login", json={"email": "asha@example.com", "password": "WrongPass999"})
    assert response.status_code == 401


def test_login_unknown_email():
    response = client.post("/login", json={"email": "nobody@example.com", "password": "MySecret123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_without_token():
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_bad_token():
    response = client.get("/me", headers={"Authorization": "Bearer garbage"})
    assert response.status_code == 401


def test_me_with_valid_token():
    client.post("/register", json={"email": "asha@example.com", "password": "MySecret123"})
    login = client.post("/login", json={"email": "asha@example.com", "password": "MySecret123"})
    token = login.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "asha@example.com"
    assert "password_hash" not in response.json()


def make_headers(email="asha@example.com"):
    client.post("/register", json={"email": email, "password": "MySecret123"})
    login = client.post("/login", json={"email": email, "password": "MySecret123"})
    return {"Authorization": "Bearer " + login.json()["access_token"]}


def test_transactions_require_login():
    assert client.get("/transactions").status_code == 401
    assert client.get("/summary").status_code == 401


def test_add_and_get_transaction():
    headers = make_headers()
    body = {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000}
    assert client.post("/transactions", json=body, headers=headers).status_code == 201

    response = client.get("/transactions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 80000


def test_bad_transaction_rejected():
    headers = make_headers()
    body = {"date": "2026-10-01", "category": "salary", "kind": "gift", "amount": 80000}
    assert client.post("/transactions", json=body, headers=headers).status_code == 422


def test_negative_amount_rejected():
    headers = make_headers()
    body = {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": -5}
    assert client.post("/transactions", json=body, headers=headers).status_code == 422


def test_users_are_isolated():
    asha = make_headers("asha@example.com")
    ravi = make_headers("ravi@example.com")
    body = {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000}
    client.post("/transactions", json=body, headers=asha)

    assert len(client.get("/transactions", headers=asha).json()) == 1
    assert client.get("/transactions", headers=ravi).json() == []


def test_summary():
    headers = make_headers()
    client.post("/transactions", json={"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000}, headers=headers)
    client.post("/transactions", json={"date": "2026-10-03", "category": "rent", "kind": "expense", "amount": 20000}, headers=headers)

    data = client.get("/summary", headers=headers).json()
    assert len(data) == 1
    assert data[0]["savings"] == 60000
    assert data[0]["savings_rate_percent"] == 75.0

def test_cors_allows_frontend():
    response = client.options(
        "/emi",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_blocks_other_origin():
    response = client.options(
        "/emi",
        headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in response.headers

def test_simulate_income_change_ok():
    response = client.get(
        "/simulate/income-change",
        params={"monthly_income": 80000, "monthly_expenses": 40000, "income_change_percent": -25},
    )
    assert response.status_code == 200
    assert response.json()["after"]["savings"] == 20000
    assert response.json()["after"]["savings_rate_percent"] == 33.33


def test_simulate_income_change_bad_percent():
    response = client.get(
        "/simulate/income-change",
        params={"monthly_income": 80000, "monthly_expenses": 40000, "income_change_percent": -101},
    )
    assert response.status_code == 422

def test_simulate_loan_ok():
    response = client.get(
        "/simulate/loan",
        params={
            "monthly_income": 80000,
            "monthly_expenses": 40000,
            "loan_amount": 500000,
            "annual_rate_percent": 10,
            "tenure_months": 60,
        },
    )
    assert response.status_code == 200
    assert response.json()["emi"] == 10623.52
    assert response.json()["verdict"] == "ok"


def test_simulate_loan_bad_input():
    response = client.get(
        "/simulate/loan",
        params={
            "monthly_income": 80000,
            "monthly_expenses": 40000,
            "loan_amount": -500000,
            "annual_rate_percent": 10,
            "tenure_months": 60,
        },
    )
    assert response.status_code == 422

def test_next_best_action_ok():
    response = client.get(
        "/next-best-action",
        params={
            "monthly_income": 80000,
            "monthly_expenses": 40000,
            "monthly_emi": 10000,
            "emergency_fund": 60000,
        },
    )
    assert response.status_code == 200
    assert response.json()["action"] == "SAVE"
    assert response.json()["details"]["emergency_fund_target"] == 120000


def test_next_best_action_bad_input():
    response = client.get(
        "/next-best-action",
        params={
            "monthly_income": 0,
            "monthly_expenses": 40000,
            "monthly_emi": 10000,
            "emergency_fund": 60000,
        },
    )
    assert response.status_code == 422


def test_login_locked_after_five_failures():
    client.post("/register", json={"email": "asha@example.com", "password": "MySecret123"})
    wrong = {"email": "asha@example.com", "password": "WrongPass999"}

    for i in range(5):
        assert client.post("/login", json=wrong).status_code == 401

    # now locked, even with the CORRECT password
    right = {"email": "asha@example.com", "password": "MySecret123"}
    assert client.post("/login", json=right).status_code == 429


def test_successful_login_resets_failures():
    client.post("/register", json={"email": "asha@example.com", "password": "MySecret123"})
    wrong = {"email": "asha@example.com", "password": "WrongPass999"}
    right = {"email": "asha@example.com", "password": "MySecret123"}

    for i in range(4):
        client.post("/login", json=wrong)
    assert client.post("/login", json=right).status_code == 200

    for i in range(4):
        assert client.post("/login", json=wrong).status_code == 401

needs_model = pytest.mark.skipif(fraud.artifact is None, reason="Run ml/train_final.py first")


def test_fraud_score_requires_login():
    response = client.get(
        "/fraud-score",
        params={"amount": 450, "hour": 14, "is_foreign": 0, "txns_last_24h": 2},
    )
    assert response.status_code == 401


@needs_model
def test_fraud_score_ok():
    headers = make_headers()
    response = client.get(
        "/fraud-score",
        params={"amount": 9000, "hour": 2, "is_foreign": 1, "txns_last_24h": 8},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["flagged"] is True


def test_fraud_score_bad_hour():
    headers = make_headers()
    response = client.get(
        "/fraud-score",
        params={"amount": 450, "hour": 24, "is_foreign": 0, "txns_last_24h": 2},
        headers=headers,
    )
    assert response.status_code == 422