import datetime
import jwt
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