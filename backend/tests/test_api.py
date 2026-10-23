from fastapi.testclient import TestClient
from app.main import app

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