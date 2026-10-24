from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hasher = PasswordHasher()


def hash_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return hasher.hash(password)


def check_password(password, stored_hash):
    try:
        return hasher.verify(stored_hash, password)
    except VerifyMismatchError:
        return False