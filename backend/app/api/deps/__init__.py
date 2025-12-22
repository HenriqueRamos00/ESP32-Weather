from app.api.deps.db import AsyncSessionDep, get_db

from app.api.deps.api_auth import (
    ApiKeyDep,
    AuthenticatedDeviceDep,
    SensorDeviceDep,
    DisplayDeviceDep,
    get_api_key,
    get_authenticated_device,
    get_sensor_device,
    get_display_device,
)

from app.api.deps.jwt_auth import (
    AdminDep,
    AdminOrUserDep,
    get_current_active_user,
    require_role
)

from app.api.deps.localhost_only import (
    LocalhostDep,
    localhost_only
)

__all__ = [
    "AsyncSessionDep",
    "ApiKeyDep",
    "AuthenticatedDeviceDep", 
    "SensorDeviceDep",
    "DisplayDeviceDep",
    "get_db",
    "get_api_key",
    "get_authenticated_device",
    "get_sensor_device",
    "get_display_device",
    "get_current_active_user",
    "require_role",
    "AdminDep",
    "AdminOrUserDep",
    "LocalhostDep",
    "localhost_only"
]