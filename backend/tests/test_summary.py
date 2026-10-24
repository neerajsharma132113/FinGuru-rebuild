from app.services.finance import summarize_by_month

SAMPLE = [
    {"date": "2026-10-01", "category": "salary", "kind": "income", "amount": 80000},
    {"date": "2026-10-03", "category": "groceries", "kind": "expense", "amount": 20000},
    {"date": "2026-10-10", "category": "rent", "kind": "expense", "amount": 20000},
    {"date": "2026-11-01", "category": "salary", "kind": "income", "amount": 80000},
]


def test_two_months():
    result = summarize_by_month(SAMPLE)
    assert len(result) == 2
    assert result[0]["month"] == "2026-10"
    assert result[0]["expenses"] == 40000
    assert result[0]["savings"] == 40000
    assert result[0]["savings_rate_percent"] == 50.0
    assert result[1]["savings_rate_percent"] == 100.0


def test_month_without_income():
    data = [{"date": "2026-12-05", "category": "food", "kind": "expense", "amount": 500}]
    result = summarize_by_month(data)
    assert result[0]["savings"] == -500
    assert result[0]["savings_rate_percent"] is None


def test_empty_list():
    assert summarize_by_month([]) == []