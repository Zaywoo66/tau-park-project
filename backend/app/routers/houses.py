# app/routers/houses.py
# House (glamping unit) endpoints:
#   GET    /api/houses        — list houses with pagination & capacity filter (public)
#   GET    /api/houses/{id}   — get a single house (public)
#   POST   /api/houses        — create a house (admin only)
#   PATCH  /api/houses/{id}   — update a house (admin only)
#   DELETE /api/houses/{id}   — delete a house (admin only)

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.booking import Booking, Status as BookingStatus
from app.models.house import House
from app.models.user import User
from app.schemas.house import HouseCreate, HouseResponse, HouseUpdate, PaginatedHousesResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/houses", tags=["Houses"])


@router.get(
    "",
    response_model=PaginatedHousesResponse,
    summary="List glamping houses with pagination and filters (public)",
)
async def list_houses(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    min_capacity: int | None = Query(None, ge=1, description="Minimum guest capacity"),
    max_capacity: int | None = Query(None, ge=1, description="Maximum guest capacity"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedHousesResponse:
    """
    Return paginated glamping units, optionally filtered by capacity.

    Query params:
      - **limit**: page size (1–100, default 20)
      - **offset**: pagination offset (default 0)
      - **min_capacity**: include only houses with capacity >= this value
      - **max_capacity**: include only houses with capacity <= this value

    This is a public endpoint — no authentication required.
    """
    try:
        query = select(House)
        count_query = select(func.count()).select_from(House)

        if min_capacity is not None:
            query = query.where(House.capacity >= min_capacity)
            count_query = count_query.where(House.capacity >= min_capacity)

        if max_capacity is not None:
            query = query.where(House.capacity <= max_capacity)
            count_query = count_query.where(House.capacity <= max_capacity)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        result = await db.execute(
            query.order_by(House.createdAt.desc()).offset(offset).limit(limit)
        )
        houses = result.scalars().all()

        return PaginatedHousesResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[HouseResponse.model_validate(h) for h in houses],
        )
    except SQLAlchemyError as exc:
        logger.error("DB error listing houses: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve houses. Please try again later.",
        )


@router.get(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Get a single glamping house by ID (public)",
)
async def get_house(
    house_id: str,
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    """Return details for one specific house. Public endpoint."""
    try:
        result = await db.execute(select(House).where(House.id == house_id))
        house = result.scalars().first()
    except SQLAlchemyError as exc:
        logger.error("DB error fetching house %s: %s", house_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve house. Please try again later.",
        )

    if house is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"House '{house_id}' not found",
        )
    return HouseResponse.model_validate(house)


@router.post(
    "",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Create a new glamping house",
)
async def create_house(
    body: HouseCreate,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    """Create a new glamping unit. Admin only."""
    try:
        # Check for duplicate name
        result = await db.execute(select(House).where(House.name == body.name))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A house named '{body.name}' already exists",
            )

        house = House(**body.model_dump())
        db.add(house)
        await db.flush()
        return HouseResponse.model_validate(house)

    except HTTPException:
        raise
    except IntegrityError as exc:
        logger.error("Integrity error creating house: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A house named '{body.name}' already exists",
        )
    except SQLAlchemyError as exc:
        logger.error("DB error creating house: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create house. Please try again later.",
        )


@router.patch(
    "/{house_id}",
    response_model=HouseResponse,
    summary="[Admin] Update a glamping house",
)
async def update_house(
    house_id: str,
    body: HouseUpdate,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    """Partially update a house's details. Admin only."""
    try:
        result = await db.execute(select(House).where(House.id == house_id))
        house = result.scalars().first()
        if house is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House '{house_id}' not found",
            )

        # Apply only provided (non-None) fields
        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(house, field, value)

        await db.flush()
        return HouseResponse.model_validate(house)

    except HTTPException:
        raise
    except IntegrityError as exc:
        logger.error("Integrity error updating house %s: %s", house_id, exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A house with this name already exists",
        )
    except SQLAlchemyError as exc:
        logger.error("DB error updating house %s: %s", house_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update house. Please try again later.",
        )


@router.delete(
    "/{house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Admin] Delete a glamping house",
)
async def delete_house(
    house_id: str,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a house. Admin only.

    Safety check: refuses deletion if the house has active (PENDING or PAID)
    bookings to prevent data inconsistency. Cancel those bookings first.
    """
    try:
        result = await db.execute(select(House).where(House.id == house_id))
        house = result.scalars().first()
        if house is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House '{house_id}' not found",
            )

        # Guard: check for active bookings before deleting
        active_bookings_result = await db.execute(
            select(func.count())
            .select_from(Booking)
            .where(
                Booking.houseId == house_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.PAID]),
            )
        )
        active_count = active_bookings_result.scalar_one()
        if active_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Cannot delete house '{house_id}': it has {active_count} active "
                    f"booking(s). Cancel all active bookings first."
                ),
            )

        await db.delete(house)

    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("DB error deleting house %s: %s", house_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete house. Please try again later.",
        )
