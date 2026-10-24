import pytest
from app.security import hash_password, check_password


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