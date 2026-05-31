import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from core.config import settings
from jose import ExpiredSignatureError, JWTError, jwt

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("ascii")


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("ascii"),
        )
    except (ValueError, TypeError):
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_session_key() -> str:
    return secrets.token_urlsafe(32)


def _get_secret_key() -> str:
    secret_key = settings.SECRET_KEY
    if not secret_key:
        raise ValueError("SECRET_KEY is not configured")
    return secret_key


def _encode_token(data: dict, expires_delta: timedelta, token_type: str):
    now = datetime.utcnow()
    payload = data.copy()
    payload.update(
        {
            "typ": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }
    )
    return jwt.encode(payload, _get_secret_key(), algorithm=settings.ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return _encode_token(
        data,
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ACCESS_TOKEN_TYPE,
    )


def create_refresh_token(data: dict, expires_delta: timedelta):
    return _encode_token(data, expires_delta, REFRESH_TOKEN_TYPE)


def decode_token(token: str):
    try:
        return jwt.decode(token, _get_secret_key(), algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError:
        raise ValueError("Invalid token")


def decode_access_token(token: str):
    payload = decode_token(token)
    if payload.get("typ") not in (None, ACCESS_TOKEN_TYPE):
        raise ValueError("Invalid token type")
    return payload


def decode_refresh_token(token: str):
    payload = decode_token(token)
    if payload.get("typ") != REFRESH_TOKEN_TYPE:
        raise ValueError("Invalid token type")
    return payload
