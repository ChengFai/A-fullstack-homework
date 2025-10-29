from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
JWT_EXPIRES_MINUTES = 60 * 24


def create_access_token(subject: str, claims: Dict[str, Any] | None = None) -> str:
    to_encode: Dict[str, Any] = {"sub": subject, "iat": datetime.now(timezone.utc)}
    if claims:
        to_encode.update(claims)
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
