"""Real API and PostgreSQL controls for registration and booking behavior."""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import asyncpg


def register(client):
    identity = uuid4().hex
    body = {
        "email": f"user-{identity}@example.com",
        "phone": "+77" + str(uuid4().int % 1_000_000_000).zfill(9),
        "password": "TestPassword!42",
    }
    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == body["email"]
    assert data["access_token"] and data["refresh_token"]
    return body, data


def headers(data):
    return {"Authorization": f"Bearer {data['access_token']}"}


def test_register_login_duplicate_and_wrong_password(client):
    body, registered = register(client)
    assert client.post("/api/auth/register", json=body).status_code == 409

    login = client.post(
        "/api/auth/login",
        json={"email": body["email"], "password": body["password"]},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["id"] == registered["user"]["id"]

    wrong = client.post(
        "/api/auth/login",
        json={"email": body["email"], "password": "wrong-password"},
    )
    assert wrong.status_code == 401
    assert body["password"] not in wrong.text
    assert "wrong-password" not in wrong.text


def test_booking_price_overlap_owner_and_cancellation(client):
    from conftest import test_url

    _, admin = register(client)

    async def promote_admin():
        connection = await asyncpg.connect(test_url.replace("postgresql+asyncpg://", "postgresql://", 1))
        try:
            await connection.execute(
                "UPDATE users SET role='ADMIN'::role_enum WHERE id=$1",
                admin["user"]["id"],
            )
        finally:
            await connection.close()

    asyncio.run(promote_admin())
    house = client.post(
        "/api/houses",
        headers=headers(admin),
        json={
            "name": "Test cabin " + uuid4().hex,
            "description": "Disposable test cabin for booking controls.",
            "price": 45000,
            "capacity": 4,
            "images": [],
        },
    )
    assert house.status_code == 201, house.text

    _, guest = register(client)
    check_in = (datetime.now(timezone.utc) + timedelta(days=7)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    booking_body = {
        "houseId": house.json()["id"],
        "checkIn": check_in.isoformat(),
        "checkOut": (check_in + timedelta(days=2)).isoformat(),
    }
    assert client.post("/api/bookings", json=booking_body).status_code in (401, 403)
    created = client.post("/api/bookings", headers=headers(guest), json=booking_body)
    assert created.status_code == 201, created.text
    booking = created.json()
    assert booking["totalPrice"] == 90000
    assert booking["status"] == "PENDING"

    conflict = client.post("/api/bookings", headers=headers(guest), json=booking_body)
    assert conflict.status_code == 409, conflict.text

    _, stranger = register(client)
    denied = client.get(f"/api/bookings/{booking['id']}", headers=headers(stranger))
    assert denied.status_code == 403

    cancelled = client.patch(f"/api/bookings/{booking['id']}/cancel", headers=headers(guest))
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "CANCELLED"
    replacement = client.post("/api/bookings", headers=headers(guest), json=booking_body)
    assert replacement.status_code == 201, replacement.text

