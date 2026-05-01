import os
from datetime import datetime, timedelta
from typing import Any, Dict
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretchangeme")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "3600"))


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(seconds=EXPIRATION_SECONDS),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    return payload
