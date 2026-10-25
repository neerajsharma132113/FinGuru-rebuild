import pytest
from app.services.finance import next_best_action


def test_no_action():
    result = next_best_action(80000, 40000, 10000, 300000)
    assert result["action"] == "NO ACTION"
    assert result["details"]["emi_to_income_percent"] == 12.5


def test_save_when_fund_is_low():
    result = next_best_action(80000, 40000, 10000, 60000)
    assert result["action"] == "SAVE"
    assert result["details"]["emergency_fund_target"] == 120000


def test_warn_when_emi_is_high():
    result = next_best_action(50000, 20000, 25000, 500000)
    assert result["action"] == "WARN"
    assert result["details"]["emi_to_income_percent"] == 50.0


def test_help_when_spending_exceeds_income():
    result = next_best_action(30000, 35000, 5000, 100000)
    assert result["action"] == "HELP"


def test_emi_exactly_at_limit_is_not_warned():
    result = next_best_action(50000, 30000, 20000, 500000)
    assert result["action"] == "NO ACTION"


def test_help_has_priority_over_warn():
    result = next_best_action(30000, 35000, 20000, 0)
    assert result["action"] == "HELP"


def test_bad_income():
    with pytest.raises(ValueError):
        next_best_action(0, 1000, 0, 0)


def test_negative_fund():
    with pytest.raises(ValueError):
        next_best_action(50000, 20000, 0, -1)