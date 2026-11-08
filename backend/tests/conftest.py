"""Run API tests only against an explicitly named disposable PostgreSQL DB."""

import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url


backend = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend))

test_url = os.environ.get("TEST_DATABASE_URL", "")
try:
    parsed = make_url(test_url)
except Exception as exc:
    raise RuntimeError("Set TEST_DATABASE_URL to a dedicated tau_park_test database") from exc
if parsed.drivername != "postgresql+asyncpg" or parsed.database != "tau_park_test":
    raise RuntimeError("Tests refuse a database other than PostgreSQL tau_park_test")

os.environ["DATABASE_URL"] = test_url
os.environ.setdefault("SECRET_KEY", "test-only-key-never-use-for-a-real-deployment")

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client

