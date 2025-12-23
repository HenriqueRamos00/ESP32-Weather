from datetime import datetime
from pydantic import BaseModel

class Timestamp(BaseModel):
    timestamp: datetime