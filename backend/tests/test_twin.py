import pytest
from app.services.finance import simulate_income_change


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