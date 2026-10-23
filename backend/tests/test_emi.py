import pytest
from app.services.finance import calculate_emi, calculate_schedule


def test_normal_loan():
    result = calculate_emi(500000, 10, 60)
    assert result["emi"] == 10623.52
    assert result["total_payment"] == 637411.34
    assert result["total_interest"] == 137411.34


def test_zero_interest():
    result = calculate_emi(500000, 0, 60)
    assert result["emi"] == 8333.33


def test_negative_principal_rejected():
    with pytest.raises(ValueError):
        calculate_emi(-1000, 10, 60)


def test_negative_rate_rejected():
    with pytest.raises(ValueError):
        calculate_emi(500000, -1, 60)


def test_zero_tenure_rejected():
    with pytest.raises(ValueError):
        calculate_emi(500000, 10, 0)


def test_schedule_length_and_end_balance():
    schedule = calculate_schedule(500000, 10, 60)
    assert len(schedule) == 60
    assert schedule[-1]["balance"] == 0


def test_schedule_first_month():
    first = calculate_schedule(500000, 10, 60)[0]
    assert first["interest"] == 4166.67
    assert first["principal_paid"] == 6456.85
    assert first["balance"] == 493543.15


def test_schedule_principal_adds_up():
    schedule = calculate_schedule(500000, 10, 60)
    total_principal = sum(row["principal_paid"] for row in schedule)
    assert round(total_principal, 2) == 500000