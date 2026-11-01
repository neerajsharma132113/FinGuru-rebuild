from app.config import parse_origins


def test_parse_origins_splits_and_trims():
    assert parse_origins("http://a.com, http://b.com ,") == ["http://a.com", "http://b.com"]


def test_parse_origins_empty():
    assert parse_origins("") == []