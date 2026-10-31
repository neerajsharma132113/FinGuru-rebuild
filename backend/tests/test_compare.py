import pytest
from app.services.finance import calculate_emi, compare_loans


def test_compare_uses_calculate_emi():
    result = compare_loans(500000, 10, 60, 10, 36)
    assert result["a"] == calculate_emi(500000, 10, 60)
    assert result["b"] == calculate_emi(500000, 10, 36)


def test_shorter_tenure_has_higher_emi_but_lower_interest():
    result = compare_loans(500000, 10, 60, 10, 36)
    assert result["emi_difference"] > 0
    assert result["total_interest_difference"] < 0
    assert result["lower_total_cost"] == "b"


def test_same_loan_is_same():
    result = compare_loans(500000, 10, 60, 10, 60)
    assert result["emi_difference"] == 0
    assert result["total_interest_difference"] == 0
    assert result["lower_total_cost"] == "same"


def test_compare_bad_input():
    with pytest.raises(ValueError):
        compare_loans(500000, 10, 60, -1, 36)