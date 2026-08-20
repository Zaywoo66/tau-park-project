# app/services/booking_service.py
# Core business logic for bookings:
#   - Availability check (overlap detection)
#   - Total price calculation

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, Status


async def check_house_availability(
    db: AsyncSession,
    house_id: str,
    check_in: datetime,
    check_out: datetime,
    exclude_booking_id: str | None = None,
) -> bool:
    """
    Return True if the house is available for the requested date range.

    Overlap condition (standard interval overlap logic):
        An existing booking CONFLICTS if:
            existing.checkIn  < requested.checkOut
            AND
            existing.checkOut > requested.checkIn

    The `exclude_booking_id` parameter allows re-checking availability
    when modifying an existing booking (its own dates should not block itself).
    """
    query = select(Booking).where(
        and_(
            Booking.houseId == house_id,
            Booking.status != Status.CANCELLED,   # Cancelled bookings free up dates
            Booking.checkIn < check_out,
            Booking.checkOut > check_in,
        )
    )

    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)

    result = await db.execute(query)
    conflicting = result.scalars().first()
    return conflicting is None  # True = available, False = conflicting booking exists


def calculate_total_price(price_per_night: int, check_in: datetime, check_out: datetime) -> int:
    """
    Calculate the total booking price.

    Formula: price_per_night × number_of_nights
    Minimum 1 night is enforced (ceil ensures same-day check-in/out = 1 night).
    """
    nights = (check_out.date() - check_in.date()).days
    if nights < 1:
        nights = 1
    return price_per_night * nights
