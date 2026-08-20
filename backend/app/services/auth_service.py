# app/services/auth_service.py
# All authentication logic: password hashing, JWT creation and verification.
# Kept separate from routers to keep business logic testable and reusable.

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ── Password Hashing ──────────────────────────────────────────────────────────
# bcrypt is the industry standard for password storage.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Utilities ─────────────────────────────────────────────────────────────

def _create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Internal helper — create a signed JWT with an expiry claim.
    `data` should contain at minimum {"sub": user_id, "type": "access"|"refresh"}.
    """
    payload = data.copy()
    expire = datetime.now(tz=timezone.utc) + expires_delta
    payload.update({"exp": expire, "iat": datetime.now(tz=timezone.utc)})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str) -> str:
    """
    Create a short-lived access token (default: 30 minutes).
    Used to authenticate every API request.
    """
    return _create_token(
        data={"sub": user_id, "type": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """
    Create a long-lived refresh token (default: 30 days).
    Used only to obtain a new access token via POST /api/auth/refresh.
    """
    return _create_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT. Raises JWTError on invalid/expired tokens.
    Returns the full payload dict.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def extract_user_id(token: str, expected_type: str = "access") -> str:
    """
    Convenience wrapper — decode a token and return the `sub` (user ID).
    Raises ValueError if the token type does not match `expected_type`.
    Raises JWTError if the token is invalid or expired.
    """
    payload = decode_token(token)
    token_type: str | None = payload.get("type")
    if token_type != expected_type:
        raise ValueError(
            f"Expected token type '{expected_type}', got '{token_type}'"
        )
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise ValueError("Token is missing 'sub' claim")
    return user_id
