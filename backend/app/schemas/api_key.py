from datetime import datetime
from typing import Sequence
from pydantic import BaseModel, ConfigDict


class ApiKeyBase(BaseModel):
    name: str
    device_id: int


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyInDB(ApiKeyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    last_used: datetime | None
    created_at: datetime


class ApiKey(ApiKeyInDB):
    """API Key without the actual key value (for listing)."""
    pass


class ApiKeyWithSecret(ApiKeyInDB):
    """API Key with the actual key value (only returned on creation)."""
    key: str


class ApiKeyList(BaseModel):
    api_keys: Sequence[ApiKey]
    total: int