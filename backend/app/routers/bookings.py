# app/routers/bookings.py
# Booking endpoints:
#   POST   /api/bookings              — create a booking (authenticated)
#   GET    /api/bookings              — list my bookings with pagination (authenticated)
#   GET    /api/bookings/all          — list all bookings (admin only)
#   GET    /api/bookings/{id}         — get a single booking (owner or admin)
#   PATCH  /api/bookings/{id}/cancel  — cancel a booking (owner or admin)
#
# IMPORTANT: Static path "/all" MUST be declared before dynamic "/{booking_id}"
# to prevent FastAPI from treating "all" as a booking ID.

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.booking import Booking, Status
from app.models.house import House
from app.models.user import Role, User
from app.schemas.booking import (
    BookingResponse,
    CreateBookingRequest,
    PaginatedBookingsResponse,
    Status as SchemaStatus,
)
from app.services.booking_service import calculate_total_price, check_house_availability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
)
async def create_booking(
    body: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Create a booking for an authenticated user.

    Server-side logic:
      1. Verify the house exists.
      2. Check no overlapping PENDING/PAID bookings exist for the date range.
         Returns **409 Conflict** if the house is already booked.
      3. Calculate totalPrice = house.price × nights.
      4. Persist and return the new booking with house details.
    """
    try:
        # 1. Verify house exists
        result = await db.execute(select(House).where(House.id == body.houseId))
        house = result.scalars().first()
        if house is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House '{body.houseId}' not found",
            )

        # Serialize bookings for this house until the request transaction commits.
        # Without this lock, two concurrent requests can both observe availability.
        await db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:house_id, 0))"),
            {"house_id": body.houseId},
        )

        # 2. Availability check — strict overlap detection via DB query
        is_available = await check_house_availability(
            db=db,
            house_id=body.houseId,
            check_in=body.checkIn,
            check_out=body.checkOut,
        )
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The house is already booked for the selected dates. "
                    "Please choose different dates."
                ),
            )

        # 3. Calculate price server-side (prevents client-side tampering)
        total_price = calculate_total_price(house.price, body.checkIn, body.checkOut)

        # 4. Create booking
        booking = Booking(
            userId=current_user.id,
            houseId=body.houseId,
            checkIn=body.checkIn,
            checkOut=body.checkOut,
            totalPrice=total_price,
        )
        db.add(booking)
        await db.flush()

        # Reload with house relation for the response
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.house))
            .where(Booking.id == booking.id)
        )
        booking = result.scalars().one()
        return BookingResponse.model_validate(booking)

    except HTTPException:
        raise
    except IntegrityError as exc:
        logger.error("Integrity error creating booking: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking could not be created due to a data conflict.",
        )
    except SQLAlchemyError as exc:
        logger.error("DB error creating booking: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking. Please try again later.",
        )


@router.get(
    "",
    response_model=PaginatedBookingsResponse,
    summary="List my bookings (paginated)",
)
async def list_my_bookings(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    booking_status: SchemaStatus | None = Query(
        None, alias="status", description="Filter by booking status"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedBookingsResponse:
    """
    Return paginated bookings belonging to the currently authenticated user.

    Query params:
      - **limit**: page size (1–100, default 20)
      - **offset**: pagination offset (default 0)
      - **status**: optional filter — PENDING | PAID | CANCELLED
    """
    try:
        base_filter = [Booking.userId == current_user.id]
        if booking_status is not None:
            # Map schema Status to model Status
            base_filter.append(Booking.status == Status(booking_status.value))

        count_result = await db.execute(
            select(func.count()).select_from(Booking).where(*base_filter)
        )
        total = count_result.scalar_one()

        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.house))
            .where(*base_filter)
            .order_by(Booking.createdAt.desc())
            .offset(offset)
            .limit(limit)
        )
        bookings = result.scalars().all()

        return PaginatedBookingsResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[BookingResponse.model_validate(b) for b in bookings],
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing bookings for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings. Please try again later.",
        )


@router.get(
    "/all",
    response_model=PaginatedBookingsResponse,
    summary="[Admin] List all bookings (paginated)",
)
async def list_all_bookings(
    limit: int = Query(50, ge=1, le=200, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    booking_status: SchemaStatus | None = Query(
        None, alias="status", description="Filter by booking status"
    ),
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> PaginatedBookingsResponse:
    """
    Return all bookings across all users, paginated. Admin only.
    Eagerly loads both `house` and `user` relations for a complete response.
    """
    try:
        filters = []
        if booking_status is not None:
            filters.append(Booking.status == Status(booking_status.value))

        count_result = await db.execute(
            select(func.count()).select_from(Booking).where(*filters)
        )
        total = count_result.scalar_one()

        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.house), selectinload(Booking.user))
            .where(*filters)
            .order_by(Booking.createdAt.desc())
            .offset(offset)
            .limit(limit)
        )
        bookings = result.scalars().all()

        return PaginatedBookingsResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[BookingResponse.model_validate(b) for b in bookings],
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing all bookings (admin): %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings. Please try again later.",
        )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get a single booking by ID",
)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Return a specific booking. Accessible by the booking's owner or an admin.
    """
    try:
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.house))
            .where(Booking.id == booking_id)
        )
        booking = result.scalars().first()
    except SQLAlchemyError as exc:
        logger.error("DB error fetching booking %s: %s", booking_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve booking. Please try again later.",
        )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{booking_id}' not found",
        )

    # Authorisation: owner or admin
    if booking.userId != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this booking",
        )

    return BookingResponse.model_validate(booking)


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    summary="Cancel a booking",
)
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Cancel a booking. Accessible by the booking owner or an admin.
    Only PENDING or PAID bookings can be cancelled.
    """
    try:
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.house))
            .where(Booking.id == booking_id)
        )
        booking = result.scalars().first()

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking '{booking_id}' not found",
            )

        # Authorisation: owner or admin
        if booking.userId != current_user.id and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this booking",
            )

        if booking.status == Status.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This booking is already cancelled",
            )

        booking.status = Status.CANCELLED
        await db.flush()
        return BookingResponse.model_validate(booking)

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("DB error cancelling booking %s: %s", booking_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking. Please try again later.",
        )
