# app/main.py
# FastAPI application entry point.
# Registers middleware, CORS, routers, startup/shutdown events,
# and global exception handlers for clean JSON error responses.

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import Base, engine
from app.routers import auth, bookings, houses, users

logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: create all database tables if they don't exist.
    (In production, prefer Alembic migrations over auto-create.)
    """
    async with engine.begin() as conn:
        # Import all models so Base.metadata knows about them
        import app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: dispose the engine connection pool cleanly
    await engine.dispose()


# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "RESTful API for the TAU-PARK glamping reservation system. "
        "Provides endpoints for user authentication, glamping house listings, "
        "and booking management with real-time availability checking."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ─────────────────────────────────────────────────

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Catch any unhandled SQLAlchemy/asyncpg database error and return a
    structured JSON 500 instead of a raw Python traceback.
    """
    logger.error("Unhandled database error on %s %s: %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Override FastAPI's default 422 handler to return a cleaner error format
    compatible with the frontend error-handling logic.
    """
    errors = [
        {"field": " -> ".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
API = settings.API_PREFIX   # "/api"

app.include_router(auth.router,     prefix=API)
app.include_router(users.router,    prefix=API)
app.include_router(houses.router,   prefix=API)
app.include_router(bookings.router, prefix=API)


# ── Root Health Check ─────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="API health check")
async def root() -> JSONResponse:
    """Simple health check endpoint — confirms the API is running."""
    return JSONResponse(
        content={
            "status": "ok",
            "project": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": "/docs",
        }
    )
