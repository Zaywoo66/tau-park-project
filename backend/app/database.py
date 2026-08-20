# app/database.py
# Async SQLAlchemy engine + session factory.
# All DB interaction flows through the AsyncSession provided by get_db().

from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────
# echo=True prints SQL to stdout (useful during development, disable in production)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,   # Verify connections before use (prevents stale connections)
    pool_size=10,
    max_overflow=20,
)

# ── Session Factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Avoids lazy-loading issues after commit
)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    - On success: commits the transaction automatically.
    - On any exception: rolls back to prevent partial writes.
    - Always: closes the session via the async context manager,
      returning the connection to the pool cleanly.

    Usage:
        db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
