from app.services.finance import health_check
from app.workflow import run_health_graph


def tx(date, kind, amount):
    return {"date": date, "category": "test", "kind": kind, "amount": amount}


CASES = {
    "two months": [
        tx("2026-10-01", "income", 80000),
        tx("2026-10-05", "expense", 40000),
        tx("2026-11-01", "income", 80000),
        tx("2026-11-05", "expense", 30000),
    ],
    "worsening": [
        tx("2026-10-01", "income", 80000),
        tx("2026-10-05", "expense", 30000),
        tx("2026-11-01", "income", 80000),
        tx("2026-11-05", "expense", 40000),
    ],
    "one month": [tx("2026-10-01", "income", 80000), tx("2026-10-05", "expense", 40000)],
    "overspending": [tx("2026-10-01", "income", 30000), tx("2026-10-05", "expense", 35000)],
    "no income": [tx("2026-10-05", "expense", 500)],
    "no data": [],
}


def test_graph_matches_plain_function():
    for name, data in CASES.items():
        plain = health_check(data, 10000, 60000)
        graph = run_health_graph(data, 10000, 60000)
        assert graph == plain, name


def test_graph_high_emi_gives_warn():
    data = [tx("2026-10-01", "income", 50000), tx("2026-10-05", "expense", 20000)]
    assert run_health_graph(data, 25000, 500000)["action"] == "WARN"