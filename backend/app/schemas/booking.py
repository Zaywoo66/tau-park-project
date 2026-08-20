# app/schemas/booking.py
# Pydantic v2 schemas for Booking.
# camelCase field names mirror Prisma output and TypeScript Booking interface.

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, model_validator

from app.schemas.house import HouseResponse
from app.schemas.user import UserResponse

# Maximum days ahead a booking can be made (business rule)
_MAX_BOOKING_HORIZON_DAYS = 365


class Status(str, Enum):
    """Mirrors Prisma enum Status and TypeScript BookingStatus type."""
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


# ── Request Schemas ───────────────────────────────────────────────────────────

class CreateBookingRequest(BaseModel):
    """
    Body for POST /api/bookings.
    The frontend sends houseId + date range; totalPrice is calculated server-side.

    Validations:
      - checkOut must be strictly after checkIn
      - checkIn must not be in the past (UTC)
      - booking horizon is capped at 365 days from today
    """
    houseId: str
    checkIn: datetime
    checkOut: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "CreateBookingRequest":
        now_utc = datetime.now(tz=timezone.utc)

        # Normalise to UTC-aware if the client sends naive datetimes
        check_in = self.checkIn
        check_out = self.checkOut
        if check_in.tzinfo is None:
            check_in = check_in.replace(tzinfo=timezone.utc)
        if check_out.tzinfo is None:
            check_out = check_out.replace(tzinfo=timezone.utc)

        if check_out <= check_in:
            raise ValueError("checkOut must be strictly after checkIn")

        if check_in < now_utc.replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValueError("checkIn cannot be in the past")

        days_ahead = (check_in.date() - now_utc.date()).days
        if days_ahead > _MAX_BOOKING_HORIZON_DAYS:
            raise ValueError(
                f"Bookings can only be made up to {_MAX_BOOKING_HORIZON_DAYS} days in advance"
            )

        return self


# ── Response Schemas ──────────────────────────────────────────────────────────

class BookingResponse(BaseModel):
    """
    Returned on any endpoint that exposes booking data.

    TypeScript equivalent:
        interface Booking {
            id: string;
            userId: string;
            houseId: string;
            checkIn: string;       // ISO 8601
            checkOut: string;      // ISO 8601
            totalPrice: number;    // KZT
            status: "PENDING" | "PAID" | "CANCELLED";
            createdAt: string;     // ISO 8601
            house?: House;         // Populated on detail/admin endpoints
            user?: User;           // Populated on admin endpoints only
        }
    """
    id: str
    userId: str
    houseId: str
    checkIn: datetime
    checkOut: datetime
    totalPrice: int
    status: Status
    createdAt: datetime
    house: HouseResponse | None = None   # Eagerly loaded on detail endpoints
    user: UserResponse | None = None     # Populated only on admin list endpoint

    model_config = {"from_attributes": True}


# ── Pagination / Filter Response ──────────────────────────────────────────────

class PaginatedBookingsResponse(BaseModel):
    """Wrapper for paginated booking list responses."""
    total: int
    limit: int
    offset: int
    items: list[BookingResponse]
