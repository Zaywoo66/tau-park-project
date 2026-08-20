# app/models/booking.py
# SQLAlchemy ORM model for the Booking entity.
# Mirrors the updated Prisma `Booking` model (now with houseId).

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Status(str, enum.Enum):
    """Booking lifecycle status — mirrors Prisma enum Status."""
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Booking(Base):
    """
    A reservation linking a User to a specific House for a date range.

    Prisma equivalent:
        model Booking { id, userId, houseId, checkIn, checkOut, totalPrice, status, createdAt }
    """
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    userId: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    houseId: Mapped[str] = mapped_column(
        String, ForeignKey("houses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    checkIn: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    checkOut: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    totalPrice: Mapped[int] = mapped_column(Integer, nullable=False)  # Pre-calculated, KZT
    status: Mapped[Status] = mapped_column(
        Enum(Status, name="status_enum", create_type=True),
        default=Status.PENDING,
        nullable=False,
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="bookings")  # noqa: F821
    house: Mapped["House"] = relationship("House", back_populates="bookings")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} houseId={self.houseId} "
            f"checkIn={self.checkIn.date()} checkOut={self.checkOut.date()} "
            f"status={self.status}>"
        )
