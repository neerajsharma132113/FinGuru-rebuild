import pytest
from app.services.finance import simulate_income_change, simulate_loan


def test_income_drop():
    result = simulate_income_change(80000, 40000, -25)
    assert result["before"]["savings"] == 40000
    assert result["before"]["savings_rate_percent"] == 50.0
    assert result["after"]["income"] == 60000
    assert result["after"]["savings"] == 20000
    assert result["after"]["savings_rate_percent"] == 33.33


def test_income_increase():
    result = simulate_income_change(80000, 40000, 10)
    assert result["after"]["income"] == 88000
    assert result["after"]["savings"] == 48000
    assert result["after"]["savings_rate_percent"] == 54.55


def test_no_savings_left():
    result = simulate_income_change(80000, 40000, -50)
    assert result["after"]["savings"] == 0
    assert result["after"]["savings_rate_percent"] == 0.0


def test_income_falls_to_zero():
    result = simulate_income_change(80000, 40000, -100)
    assert result["after"]["savings"] == -40000
    assert result["after"]["savings_rate_percent"] is None


def test_bad_income():
    with pytest.raises(ValueError):
        simulate_income_change(0, 40000, -20)


def test_bad_change():
    with pytest.raises(ValueError):
        simulate_income_change(80000, 40000, -101)

def test_loan_ok():
    result = simulate_loan(80000, 40000, 500000, 10, 60)
    assert result["emi"] == 10623.52
    assert result["emi_to_income_percent"] == 13.28
    assert result["savings_before"] == 40000
    assert result["savings_after"] == 29376.48
    assert result["savings_rate_after_percent"] == 36.72
    assert result["verdict"] == "ok"


def test_loan_stretched():
    # EMI is about 42% of income, but savings are still positive
    result = simulate_loan(50000, 20000, 1000000, 10, 60)
    assert result["savings_after"] > 0
    assert result["verdict"] == "stretched"


def test_loan_unaffordable():
    # savings would go below zero
    result = simulate_loan(50000, 40000, 500000, 10, 60)
    assert result["savings_after"] == -623.52
    assert result["verdict"] == "unaffordable"


def test_loan_bad_income():
    with pytest.raises(ValueError):
        simulate_loan(0, 0, 500000, 10, 60)


def test_loan_bad_amount():
    with pytest.raises(ValueError):
        simulate_loan(80000, 40000, -500000, 10, 60)