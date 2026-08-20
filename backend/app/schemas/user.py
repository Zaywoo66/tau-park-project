# app/schemas/user.py
# Pydantic v2 schemas for User.
# Field names are camelCase to match both the Prisma model output and
# the TypeScript interfaces consumed by the React frontend.

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    """Mirrors Prisma enum Role and TypeScript Role type."""
    USER = "USER"
    ADMIN = "ADMIN"


# ── Request Schemas ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Body for POST /api/auth/register"""
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20, pattern=r"^\+?[\d\s\-()]+$")
    password: str = Field(..., min_length=8, description="Minimum 8 characters")


class LoginRequest(BaseModel):
    """Body for POST /api/auth/login"""
    email: EmailStr
    password: str


class UpdateUserRequest(BaseModel):
    """Body for PATCH /api/users/me — all fields optional."""
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)


# ── Response Schemas ──────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """
    Returned on any endpoint that exposes user data.

    TypeScript equivalent:
        interface User {
            id: string;
            email: string;
            phone: string;
            role: "USER" | "ADMIN";
            createdAt: string; // ISO 8601
        }
    """
    id: str
    email: str
    phone: str
    role: Role
    createdAt: datetime   # serialised as ISO 8601 string by FastAPI

    model_config = {"from_attributes": True}
