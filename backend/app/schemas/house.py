# app/schemas/house.py
# Pydantic v2 schemas for House (glamping unit).
# Field names are camelCase to match Prisma output and TypeScript interfaces.

from datetime import datetime

from pydantic import BaseModel, Field


# ── Request Schemas ───────────────────────────────────────────────────────────

class HouseCreate(BaseModel):
    """Body for POST /api/houses — admin only."""
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=10)
    price: int = Field(..., gt=0, description="Per-night price in KZT (tenge)")
    capacity: int = Field(..., gt=0, le=100, description="Maximum number of guests")
    images: list[str] = Field(default_factory=list, description="List of image URLs")


class HouseUpdate(BaseModel):
    """Body for PATCH /api/houses/{id} — admin only. All fields optional."""
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    price: int | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, gt=0, le=100)
    images: list[str] | None = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class HouseResponse(BaseModel):
    """
    Returned on any endpoint that exposes house data.

    TypeScript equivalent:
        interface House {
            id: string;
            name: string;
            description: string;
            price: number;       // KZT per night
            capacity: number;    // max guests
            images: string[];
            createdAt: string;   // ISO 8601
        }
    """
    id: str
    name: str
    description: str
    price: int
    capacity: int
    images: list[str]
    createdAt: datetime

    model_config = {"from_attributes": True}


# ── Pagination Response ───────────────────────────────────────────────────────

class PaginatedHousesResponse(BaseModel):
    """Wrapper for paginated house list responses."""
    total: int
    limit: int
    offset: int
    items: list[HouseResponse]
