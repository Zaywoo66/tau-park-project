# app/schemas/auth.py
# Pydantic schemas for authentication token responses.

from pydantic import BaseModel

from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    """
    Returned after successful login or token refresh.

    TypeScript equivalent:
        interface AuthResponse {
            access_token: string;
            refresh_token: string;
            token_type: "bearer";
            user: User;
        }
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    """Body for POST /api/auth/refresh"""
    refresh_token: str
