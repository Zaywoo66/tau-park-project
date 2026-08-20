# app/models/user.py
# SQLAlchemy ORM model for the User entity.
# Mirrors the Prisma `User` model and `Role` enum exactly.

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(str, enum.Enum):
    """User role — mirrors Prisma enum Role."""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """
    System user (guest or admin).

    Prisma equivalent:
        model User { id, email, phone, password, role, createdAt, bookings[] }
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)  # bcrypt hash
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role_enum", create_type=True),
        default=Role.USER,
        nullable=False,
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    bookings: Mapped[list["Booking"]] = relationship(  # noqa: F821
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
