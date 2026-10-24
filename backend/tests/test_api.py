from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)
from app import database, security


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
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "test.db"))
    database.init_db()


def test_add_and_get_transaction():
    body = {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000}
    response = client.post("/transactions", json=body)
    assert response.status_code == 201

    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 80000


def test_bad_transaction_rejected():
    body = {"date": "2026-10-01", "category": "salary", "kind": "gift", "amount": 80000}
    response = client.post("/transactions", json=body)
    assert response.status_code == 422


def test_negative_amount_rejected():
    body = {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": -5}
    response = client.post("/transactions", json=body)
    assert response.status_code == 422


def test_summary():
    client.post("/transactions", json={"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000})
    client.post("/transactions", json={"date": "2026-10-03", "category": "rent", "kind": "expense", "amount": 20000})

    response = client.get("/summary")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["month"] == "2026-10"
    assert data[0]["savings"] == 60000
    assert data[0]["savings_rate_percent"] == 75.0

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