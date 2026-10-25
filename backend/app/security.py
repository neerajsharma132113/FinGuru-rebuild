import datetime
import jwt
import time
from app.config import SECRET_KEY
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


def create_access_token(user_id, minutes=30):
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in .env")
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def read_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload["sub"])
    except jwt.InvalidTokenError:
        return None

MAX_FAILED_ATTEMPTS = 5
LOCK_WINDOW_SECONDS = 15 * 60

failed_logins = {}  # email -> list of times of failed attempts


def get_recent_failures(email, now=None):
    if now is None:
        now = time.time()

    recent = []
    for attempt_time in failed_logins.get(email.lower(), []):
        if now - attempt_time < LOCK_WINDOW_SECONDS:
            recent.append(attempt_time)

    failed_logins[email.lower()] = recent
    return recent


def is_locked(email, now=None):
    return len(get_recent_failures(email, now)) >= MAX_FAILED_ATTEMPTS


def record_failure(email, now=None):
    if now is None:
        now = time.time()
    get_recent_failures(email, now)  # removes old attempts first
    failed_logins[email.lower()].append(now)


def clear_failures(email):
    failed_logins.pop(email.lower(), None)