from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schemas.state import StateResponse


class CityCreate(BaseModel):
    name: str
    state_id: int


class CityUpdate(BaseModel):
    name: Optional[str] = None
    state_id: Optional[int] = None
    is_active: Optional[bool] = None


class CityResponse(BaseModel):
    id: int
    name: str
    state_id: int
    state: StateResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
