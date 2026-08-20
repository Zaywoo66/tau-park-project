# app/models/house.py
# SQLAlchemy ORM model for the House (glamping unit) entity.
# Mirrors the newly added Prisma `House` model.

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class House(Base):
    """
    A glamping accommodation unit at TAU-PARK.

    Prisma equivalent:
        model House { id, name, description, price, capacity, images[], bookings[], createdAt }
    """
    __tablename__ = "houses"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)     # Per-night, KZT
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)  # Max guests
    images: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default="{}",
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    bookings: Mapped[list["Booking"]] = relationship(  # noqa: F821
        "Booking", back_populates="house", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<House id={self.id} name={self.name} price={self.price}>"
