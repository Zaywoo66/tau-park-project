# app/routers/auth.py
# Authentication endpoints:
#   POST /api/auth/register  — create a new user account
#   POST /api/auth/login     — exchange credentials for JWT pair
#   POST /api/auth/refresh   — exchange a refresh token for a new access token
#   POST /api/auth/logout    — (stateless) client discards tokens

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenResponse
from app.schemas.user import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    extract_user_id,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Create a new user account and return a JWT token pair immediately.
    The user is automatically logged in after registration.
    """
    try:
        # Check for existing email
        result = await db.execute(select(User).where(User.email == body.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        # Check for existing phone
        result = await db.execute(select(User).where(User.phone == body.phone))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists",
            )

        new_user = User(
            email=body.email,
            phone=body.phone,
            password=hash_password(body.password),
        )
        db.add(new_user)
        await db.flush()   # Flush to get the generated UUID before commit

        return TokenResponse(
            access_token=create_access_token(new_user.id),
            refresh_token=create_refresh_token(new_user.id),
            user=UserResponse.model_validate(new_user),
        )

    except HTTPException:
        raise
    except IntegrityError as exc:
        # Handles race-condition where another request registered the same email
        # between our SELECT check and the INSERT
        logger.warning("Integrity error during registration (race condition): %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or phone already exists",
        )
    except SQLAlchemyError as exc:
        logger.error("DB error during registration: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate with email + password.
    Returns an access token (30 min) and a refresh token (30 days).
    """
    try:
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalars().first()
    except SQLAlchemyError as exc:
        logger.error("DB error during login: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later.",
        )

    # Use a generic error message to avoid leaking whether the email exists
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a valid refresh token",
)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access + refresh token pair
    (token rotation — the old refresh token is effectively invalidated by
    the client replacing it with the new one).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = extract_user_id(body.refresh_token, expected_type="refresh")
    except (JWTError, ValueError):
        raise credentials_exception

    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
    except SQLAlchemyError as exc:
        logger.error("DB error during token refresh: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again later.",
        )

    if user is None:
        raise credentials_exception

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (client-side token discard)",
)
async def logout() -> None:
    """
    Stateless logout — the client is responsible for discarding the tokens.
    In a production system with a token blacklist (Redis), you would
    invalidate the refresh token here.
    """
    return None
