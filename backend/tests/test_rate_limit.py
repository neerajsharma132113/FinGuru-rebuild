import pytest
from app import security


@pytest.fixture(autouse=True)
def clean_failures():
    security.failed_logins.clear()


def test_not_locked_at_start():
    assert security.is_locked("a@example.com") is False


def test_four_failures_not_locked():
    for i in range(4):
        security.record_failure("a@example.com", now=1000 + i)
    assert security.is_locked("a@example.com", now=1010) is False


def test_five_failures_locked():
    for i in range(5):
        security.record_failure("a@example.com", now=1000 + i)
    assert security.is_locked("a@example.com", now=1010) is True


def test_lock_expires_after_window():
    for i in range(5):
        security.record_failure("a@example.com", now=1000 + i)
    assert security.is_locked("a@example.com", now=1000 + 901) is False


def test_clear_failures_unlocks():
    for i in range(5):
        security.record_failure("a@example.com", now=1000 + i)
    security.clear_failures("a@example.com")
    assert security.is_locked("a@example.com", now=1010) is False


def test_email_case_is_ignored():
    for i in range(5):
        security.record_failure("A@Example.com", now=1000 + i)
    assert security.is_locked("a@example.com", now=1010) is True