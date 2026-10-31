from app.services.finance import health_check


def tx(date, kind, amount):
    return {"date": date, "category": "test", "kind": kind, "amount": amount}


TWO_MONTHS = [
    tx("2026-10-01", "income", 80000),
    tx("2026-10-05", "expense", 40000),
    tx("2026-11-01", "income", 80000),
    tx("2026-11-05", "expense", 30000),
]


def test_health_check_ok():
    result = health_check(TWO_MONTHS, 10000, 60000)
    assert result["status"] == "ok"
    assert result["month"] == "2026-11"
    assert result["savings"] == 50000
    assert result["savings_rate_percent"] == 62.5
    assert result["savings_trend"] == "improving"
    assert result["action"] == "SAVE"
    assert result["details"]["emergency_fund_target"] == 90000


def test_health_check_worsening_trend():
    data = [
        tx("2026-10-01", "income", 80000),
        tx("2026-10-05", "expense", 30000),
        tx("2026-11-01", "income", 80000),
        tx("2026-11-05", "expense", 40000),
    ]
    assert health_check(data, 10000, 500000)["savings_trend"] == "worsening"


def test_health_check_one_month_has_no_trend():
    data = [tx("2026-10-01", "income", 80000), tx("2026-10-05", "expense", 40000)]
    result = health_check(data, 10000, 500000)
    assert result["savings_trend"] == "not enough data"
    assert result["action"] == "NO ACTION"


def test_health_check_no_data():
    assert health_check([], 0, 0)["status"] == "no_data"


def test_health_check_no_income():
    data = [tx("2026-10-05", "expense", 500)]
    assert health_check(data, 0, 0)["status"] == "no_income"