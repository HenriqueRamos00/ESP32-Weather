import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.device import DeviceType, DeviceStatus


@pytest.mark.asyncio
async def test_create_device(client: AsyncClient) -> None:
    """Test creating a device."""
    device_data = {
        "type": DeviceType.ESP32.value,
        "location": "Living Room",
        "status": DeviceStatus.ONLINE.value,
    }
    
    response = await client.post("/api/v1/devices/", json=device_data)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == device_data["type"]
    assert data["location"] == device_data["location"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_devices(client: AsyncClient) -> None:
    """Test getting all devices."""
    # Create a device first
    device_data = {
        "type": DeviceType.ESP32.value,
        "location": "Garden",
        "status": DeviceStatus.OFFLINE.value,
    }
    await client.post("/api/v1/devices/", json=device_data)
    
    # Get all devices
    response = await client.get("/api/v1/devices/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["devices"]) >= 1


@pytest.mark.asyncio
async def test_get_device(client: AsyncClient) -> None:
    """Test getting a specific device."""
    # Create a device
    device_data = {
        "type": DeviceType.ESP32_S3.value,
        "location": "Bedroom",
        "status": DeviceStatus.ONLINE.value,
    }
    create_response = await client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Get the device
    response = await client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == device_id
    assert data["location"] == device_data["location"]


@pytest.mark.asyncio
async def test_update_device(client: AsyncClient) -> None:
    """Test updating a device."""
    # Create a device
    device_data = {
        "type": DeviceType.ESP8266.value,
        "location": "Kitchen",
        "status": DeviceStatus.OFFLINE.value,
    }
    create_response = await client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Update the device
    update_data = {"location": "Garage", "status": DeviceStatus.ONLINE.value}
    response = await client.put(f"/api/v1/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == update_data["location"]
    assert data["status"] == update_data["status"]


@pytest.mark.asyncio
async def test_delete_device(client: AsyncClient) -> None:
    """Test deleting a device."""
    # Create a device
    device_data = {
        "type": DeviceType.ESP32.value,
        "location": "Basement",
        "status": DeviceStatus.OFFLINE.value,
    }
    create_response = await client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Delete the device
    response = await client.delete(f"/api/v1/devices/{device_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_device(client: AsyncClient) -> None:
    """Test getting a device that doesn't exist."""
    response = await client.get("/api/v1/devices/99999")
    assert response.status_code == 404