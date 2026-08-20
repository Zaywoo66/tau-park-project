# app/models/__init__.py
# Re-export all ORM models so that Alembic's env.py can discover them
# via a single import: `from app.models import *`

from app.models.user import User, Role        # noqa: F401
from app.models.house import House            # noqa: F401
from app.models.booking import Booking, Status  # noqa: F401
