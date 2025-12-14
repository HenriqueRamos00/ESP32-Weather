import pytest
from httpx import AsyncClient
from app.models.device import DeviceType, DeviceFunction

# Helper to create a device quickly for tests
async def create_test_device(client: AsyncClient, name_suffix: str = "") -> int:
    device_data = {
        "type": DeviceType.ESP32.value,
        "location": f"Test Location {name_suffix}",
        "function": DeviceFunction.SENSOR.value,
    }
    response = await client.post("/api/v1/devices/", json=device_data)
    return response.json()["id"]

@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient) -> None:
    """Test creating an API key for an existing device."""
    # 1. Create a device first
    device_id = await create_test_device(client)

    # 2. Create API key
    key_data = {
        "name": "Production Key",
        "device_id": device_id
    }
    response = await client.post("/api/v1/api-keys/", json=key_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify the secret key is returned ONLY on creation
    assert "key" in data
    assert len(data["key"]) > 0
    assert data["name"] == key_data["name"]
    assert data["device_id"] == device_id
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_create_api_key_nonexistent_device(client: AsyncClient) -> None:
    """Test error when creating a key for a device that doesn't exist."""
    key_data = {
        "name": "Ghost Key",
        "device_id": 99999
    }
    response = await client.post("/api/v1/api-keys/", json=key_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

@pytest.mark.asyncio
async def test_get_api_keys(client: AsyncClient) -> None:
    """Test listing all API keys."""
    device_id = await create_test_device(client)

    # Create two keys
    await client.post("/api/v1/api-keys/", json={"name": "Key 1", "device_id": device_id})
    await client.post("/api/v1/api-keys/", json={"name": "Key 2", "device_id": device_id})

    # List keys
    response = await client.get("/api/v1/api-keys/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] >= 2
    assert len(data["api_keys"]) >= 2
    
    # Ensure the secret 'key' is NOT returned in the list view
    first_key = data["api_keys"][0]
    assert "key" not in first_key

@pytest.mark.asyncio
async def test_get_device_api_keys(client: AsyncClient) -> None:
    """Test listing keys specifically for one device."""
    # Create two devices
    dev1_id = await create_test_device(client, "1")
    dev2_id = await create_test_device(client, "2")

    # Create keys for both
    await client.post("/api/v1/api-keys/", json={"name": "Dev1 Key", "device_id": dev1_id})
    await client.post("/api/v1/api-keys/", json={"name": "Dev2 Key", "device_id": dev2_id})

    # Filter by Device 1
    response = await client.get(f"/api/v1/api-keys/device/{dev1_id}")
    assert response.status_code == 200
    data = response.json()
    
    # Should only find the key for device 1
    assert data["total"] == 1
    assert data["api_keys"][0]["name"] == "Dev1 Key"
    assert data["api_keys"][0]["device_id"] == dev1_id

@pytest.mark.asyncio
async def test_get_keys_for_nonexistent_device(client: AsyncClient) -> None:
    """Test getting keys for a device ID that doesn't exist."""
    response = await client.get("/api/v1/api-keys/device/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_revoke_api_key(client: AsyncClient) -> None:
    """Test revoking an API key."""
    device_id = await create_test_device(client)
    
    # Create key
    create_res = await client.post(
        "/api/v1/api-keys/", 
        json={"name": "Key to Revoke", "device_id": device_id}
    )
    key_id = create_res.json()["id"]

    # Revoke it
    response = await client.post(f"/api/v1/api-keys/{key_id}/revoke")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["id"] == key_id

@pytest.mark.asyncio
async def test_revoke_nonexistent_key(client: AsyncClient) -> None:
    """Test revoking a key that doesn't exist."""
    response = await client.post("/api/v1/api-keys/99999/revoke")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_api_key(client: AsyncClient) -> None:
    """Test physically deleting an API key."""
    device_id = await create_test_device(client)
    
    # Create key
    create_res = await client.post(
        "/api/v1/api-keys/", 
        json={"name": "Key to Delete", "device_id": device_id}
    )
    key_id = create_res.json()["id"]

    # Delete it
    response = await client.delete(f"/api/v1/api-keys/{key_id}")
    assert response.status_code == 204

    # Verify it is gone (Revoke should fail with 404)
    check_response = await client.post(f"/api/v1/api-keys/{key_id}/revoke")
    assert check_response.status_code == 404