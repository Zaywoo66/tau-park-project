# app/routers/users.py
# User management endpoints:
#   GET    /api/users/me     — get own profile (authenticated)
#   PATCH  /api/users/me     — update own profile (authenticated)
#   GET    /api/users        — list all users (admin only)
#   DELETE /api/users/{id}   — delete user (admin only)

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UpdateUserRequest, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user's profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the currently authenticated user's profile",
)
async def update_me(
    body: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Partially update the authenticated user's email or phone.
    Only provided fields are updated (partial PATCH semantics).
    """
    try:
        if body.email is not None:
            # Ensure the new email isn't taken by another user
            result = await db.execute(
                select(User).where(User.email == body.email, User.id != current_user.id)
            )
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already in use by another account",
                )
            current_user.email = body.email

        if body.phone is not None:
            result = await db.execute(
                select(User).where(User.phone == body.phone, User.id != current_user.id)
            )
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number is already in use by another account",
                )
            current_user.phone = body.phone

        await db.flush()
        return UserResponse.model_validate(current_user)

    except HTTPException:
        raise
    except IntegrityError as exc:
        logger.warning("Integrity error updating user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone is already in use by another account",
        )
    except SQLAlchemyError as exc:
        logger.error("DB error updating user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile. Please try again later.",
        )


@router.get(
    "",
    response_model=list[UserResponse],
    summary="[Admin] List all registered users",
)
async def list_users(
    limit: int = Query(50, ge=1, le=200, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """Return a paginated list of all users. Admin only."""
    try:
        result = await db.execute(
            select(User)
            .order_by(User.createdAt.desc())
            .offset(offset)
            .limit(limit)
        )
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users]
    except SQLAlchemyError as exc:
        logger.error("DB error listing users (admin): %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users. Please try again later.",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a user account",
)
async def delete_user(
    user_id: str,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a user and all their bookings (CASCADE). Admin only."""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user_id}' not found",
            )
        await db.delete(user)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("DB error deleting user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user. Please try again later.",
        )
