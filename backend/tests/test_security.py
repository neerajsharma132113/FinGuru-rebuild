import pytest
from app.security import hash_password, check_password
from app import security
from app.security import create_access_token, read_access_token


@pytest.fixture(autouse=True)
def test_secret(monkeypatch):
    monkeypatch.setattr(security, "SECRET_KEY", "test-secret-key-for-tests-only-0123456789")


def test_token_round_trip():
    token = create_access_token(7)
    assert read_access_token(token) == 7


def test_tampered_token_rejected():
    token = create_access_token(7)
    assert read_access_token(token + "x") is None


def test_expired_token_rejected():
    token = create_access_token(7, minutes=-1)
    assert read_access_token(token) is None

def test_hash_is_not_the_password():
    hashed = hash_password("MySecret123")
    assert hashed != "MySecret123"
    assert hashed.startswith("$argon2")


def test_correct_password_accepted():
    hashed = hash_password("MySecret123")
    assert check_password("MySecret123", hashed) is True


def test_wrong_password_rejected():
    hashed = hash_password("MySecret123")
    assert check_password("WrongPass999", hashed) is False


def test_same_password_gives_different_hashes():
    assert hash_password("MySecret123") != hash_password("MySecret123")


def test_short_password_rejected():
    with pytest.raises(ValueError):
        hash_password("abc")