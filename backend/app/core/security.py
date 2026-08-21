from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_token(
    subject: str | Any,
    expires_delta: timedelta,
    *,
    token_type: str,
    jti: str | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "token_type": token_type,
    }
    if jti is not None:
        to_encode["jti"] = jti
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    return create_token(subject, expires_delta, token_type="access")


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta
) -> tuple[str, str]:
    jti = str(uuid4())
    refresh_token = create_token(subject, expires_delta, token_type="refresh", jti=jti)
    return refresh_token, jti


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
