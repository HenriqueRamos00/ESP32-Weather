import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device, DeviceType, DeviceFunction
from app.models.api_key import ApiKey  # assumes this exists

ESP32_BASE = "/api/v1/esp32"

def as_utc(dt: datetime) -> datetime:
    # SQLite often returns naive datetimes; interpret them as UTC for tests
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

async def create_device(client: AsyncClient, *, function: DeviceFunction, location: str) -> int:
    res = await client.post(
        "/api/v1/devices/",
        json={
            "type": DeviceType.ESP32.value,
            "location": location,
            "function": function.value,
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


async def create_api_key_for_device(client: AsyncClient, *, device_id: int, name: str = "Key"):
    res = await client.post(
        "/api/v1/api-keys/",
        json={"name": name, "device_id": device_id},
    )
    assert res.status_code == 201
    body = res.json()
    # Key secret is only returned on create
    assert "key" in body and body["key"]
    return {
        "id": body["id"],
        "secret": body["key"],
        "device_id": body["device_id"],
    }


def auth_headers(secret: str) -> dict[str, str]:
    return {"X-API-Key": secret}


@pytest.mark.asyncio
async def test_submit_reading_missing_api_key(client: AsyncClient) -> None:
    res = await client.post(f"{ESP32_BASE}/readings", json={"temperature": 20.5})
    assert res.status_code == 401
    assert res.json()["detail"] == "Missing API key"


@pytest.mark.asyncio
async def test_submit_reading_invalid_api_key(client: AsyncClient) -> None:
    res = await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers("not-a-real-key"),
        json={"temperature": 20.5},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid API key"


@pytest.mark.asyncio
async def test_submit_reading_with_display_key_forbidden(client: AsyncClient) -> None:
    display_device_id = await create_device(
        client, function=DeviceFunction.DISPLAY, location="Display Board"
    )
    display_key = await create_api_key_for_device(client, device_id=display_device_id)

    res = await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(display_key["secret"]),
        json={"temperature": 22.0, "humidity": 50},
    )
    assert res.status_code == 403
    assert "expected 'sensor'" in res.json()["detail"]


@pytest.mark.asyncio
async def test_submit_reading_revoked_key_unauthorized(client: AsyncClient) -> None:
    sensor_device_id = await create_device(
        client, function=DeviceFunction.SENSOR, location="Sensor Board"
    )
    sensor_key = await create_api_key_for_device(client, device_id=sensor_device_id)

    # Revoke
    revoke_res = await client.post(f"/api/v1/api-keys/{sensor_key['id']}/revoke")
    assert revoke_res.status_code == 200
    assert revoke_res.json()["is_active"] is False

    # Use revoked key
    res = await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(sensor_key["secret"]),
        json={"temperature": 18.0},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "API key has been revoked"


@pytest.mark.asyncio
async def test_submit_reading_validation_error(client: AsyncClient) -> None:
    sensor_device_id = await create_device(
        client, function=DeviceFunction.SENSOR, location="Sensor Board"
    )
    sensor_key = await create_api_key_for_device(client, device_id=sensor_device_id)

    # humidity > 100 should 422 due to schema constraints
    res = await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(sensor_key["secret"]),
        json={"temperature": 20.0, "humidity": 101},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_submit_reading_success_updates_last_seen_and_last_used(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    sensor_device_id = await create_device(
        client, function=DeviceFunction.SENSOR, location="Outdoor Sensor"
    )
    sensor_key = await create_api_key_for_device(client, device_id=sensor_device_id)

    before = datetime.now(timezone.utc)

    res = await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(sensor_key["secret"]),
        json={
            "temperature": 21.25,
            "humidity": 55.0,
            "pressure": 1001.2,
            "wind_speed": 2.5,
            "rain_amount": 0.0,
        },
    )
    assert res.status_code == 201
    body = res.json()

    assert body["device_id"] == sensor_device_id
    assert body["temperature"] == 21.25
    assert body["humidity"] == 55.0
    assert "recorded_at" in body
    assert "created_at" in body

    # Verify device.last_seen updated by auth dependency
    device = await db_session.get(Device, sensor_device_id)
    assert device is not None
    assert device.last_seen is not None
    assert as_utc(device.last_seen) >= before

    # Verify api key last_used updated (if your ApiKey model has this field)
    key_row = await db_session.get(ApiKey, sensor_key["id"])
    assert key_row is not None
    if hasattr(key_row, "last_used"):
        assert key_row.last_used is not None
        assert as_utc(key_row.last_used) >= before


@pytest.mark.asyncio
async def test_display_latest_missing_api_key(client: AsyncClient) -> None:
    res = await client.get(f"{ESP32_BASE}/display/latest")
    assert res.status_code == 401
    assert res.json()["detail"] == "Missing API key"


@pytest.mark.asyncio
async def test_display_latest_with_sensor_key_forbidden(client: AsyncClient) -> None:
    sensor_device_id = await create_device(
        client, function=DeviceFunction.SENSOR, location="Sensor"
    )
    sensor_key = await create_api_key_for_device(client, device_id=sensor_device_id)

    res = await client.get(
        f"{ESP32_BASE}/display/latest",
        headers=auth_headers(sensor_key["secret"]),
    )
    assert res.status_code == 403
    assert "expected 'display'" in res.json()["detail"]


@pytest.mark.asyncio
async def test_display_latest_success_returns_latest_per_sensor_and_updates_last_seen(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Two sensors
    s1_id = await create_device(client, function=DeviceFunction.SENSOR, location="Garden")
    s2_id = await create_device(client, function=DeviceFunction.SENSOR, location="Roof")

    s1_key = await create_api_key_for_device(client, device_id=s1_id, name="S1")
    s2_key = await create_api_key_for_device(client, device_id=s2_id, name="S2")

    # Multiple readings per sensor; display endpoint should return latest per sensor
    await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(s1_key["secret"]),
        json={"temperature": 10.0, "humidity": 40},
    )
    await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(s1_key["secret"]),
        json={"temperature": 11.0, "humidity": 41},
    )
    await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(s2_key["secret"]),
        json={"temperature": 20.0, "humidity": 50},
    )

    # Display device
    display_id = await create_device(
        client, function=DeviceFunction.DISPLAY, location="Living Room Display"
    )
    display_key = await create_api_key_for_device(client, device_id=display_id, name="Display")

    before = datetime.now(timezone.utc)

    res = await client.get(
        f"{ESP32_BASE}/display/latest",
        headers=auth_headers(display_key["secret"]),
    )
    assert res.status_code == 200
    data = res.json()

    assert "fetched_at" in data
    assert "readings" in data

    readings = data["readings"]
    # Exactly one per sensor
    device_ids = {r["device_id"] for r in readings}
    assert s1_id in device_ids
    assert s2_id in device_ids

    # Ensure latest for s1 is the second one (temp 11.0)
    s1_latest = next(r for r in readings if r["device_id"] == s1_id)
    assert s1_latest["temperature"] == 11.0
    assert s1_latest["device_location"] == "Garden"

    # Ensure device.last_seen updated for display device as well
    display_device = await db_session.get(Device, display_id)
    assert display_device is not None
    assert display_device.last_seen is not None
    assert as_utc(display_device.last_seen) >= before


@pytest.mark.asyncio
async def test_display_sensor_latest_404_when_no_readings(client: AsyncClient) -> None:
    sensor_id = await create_device(client, function=DeviceFunction.SENSOR, location="NoData Sensor")
    display_id = await create_device(client, function=DeviceFunction.DISPLAY, location="Display")
    display_key = await create_api_key_for_device(client, device_id=display_id)

    res = await client.get(
        f"{ESP32_BASE}/display/sensor/{sensor_id}/latest",
        headers=auth_headers(display_key["secret"]),
    )
    assert res.status_code == 404
    assert res.json()["detail"] == f"No readings found for device {sensor_id}"


@pytest.mark.asyncio
async def test_display_sensor_latest_success(client: AsyncClient) -> None:
    sensor_id = await create_device(client, function=DeviceFunction.SENSOR, location="Patio")
    sensor_key = await create_api_key_for_device(client, device_id=sensor_id)

    await client.post(
        f"{ESP32_BASE}/readings",
        headers=auth_headers(sensor_key["secret"]),
        json={"temperature": 23.5, "humidity": 60},
    )

    display_id = await create_device(client, function=DeviceFunction.DISPLAY, location="Display")
    display_key = await create_api_key_for_device(client, device_id=display_id)

    res = await client.get(
        f"{ESP32_BASE}/display/sensor/{sensor_id}/latest",
        headers=auth_headers(display_key["secret"]),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["device_id"] == sensor_id
    assert data["temperature"] == 23.5
    assert data["device_location"] == "Patio"