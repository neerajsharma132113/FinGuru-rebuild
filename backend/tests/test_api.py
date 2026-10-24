from fastapi.testclient import TestClient
from app.main import app
import pytest
from app import database
client = TestClient(app)


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