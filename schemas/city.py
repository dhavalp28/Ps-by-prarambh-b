from pydantic import BaseModel, ConfigDict
from typing import Optional

from schemas.state import StateResponse


class CityCreate(BaseModel):
    name: str
    state_id: int


class CityUpdate(BaseModel):
    name: Optional[str] = None
    state_id: Optional[int] = None
    is_active: Optional[bool] = None


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    state: StateResponse
    is_active: bool
