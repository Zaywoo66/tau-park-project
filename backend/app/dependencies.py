# app/dependencies.py
# Reusable FastAPI dependency functions injected via Depends().
# Centralising them here keeps routers thin and logic DRY.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import Role, User
from app.services.auth_service import extract_user_id

# HTTPBearer parses the "Authorization: Bearer <token>" header automatically
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency: validate the access token and return the authenticated User.

    Raises HTTP 401 if the token is missing, invalid, or expired.
    Raises HTTP 401 if the user no longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = extract_user_id(credentials.credentials, expected_type="access")
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: extend get_current_user to also require ADMIN role.

    Raises HTTP 403 Forbidden if the user is not an admin.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
