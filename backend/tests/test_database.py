import pytest
from app import database


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", str(tmp_path / "test.db"))
    database.init_db()


def test_add_and_list():
    database.add_transaction("2026-10-01", "salary", "income", 80000)
    database.add_transaction("2026-10-03", "groceries", "expense", 2450.50)
    rows = database.list_transactions()
    assert len(rows) == 2
    assert rows[1]["category"] == "groceries"
    assert rows[1]["amount"] == 2450.5


def test_empty_database():
    assert database.list_transactions() == []


def test_bad_kind_rejected():
    with pytest.raises(ValueError):
        database.add_transaction("2026-10-01", "x", "gift", 100)


def test_bad_amount_rejected():
    with pytest.raises(ValueError):
        database.add_transaction("2026-10-01", "x", "expense", -5)