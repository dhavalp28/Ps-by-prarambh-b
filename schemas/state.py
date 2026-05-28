from pydantic import BaseModel, ConfigDict
from typing import Optional


class StateCreate(BaseModel):
    name: str


class StateUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class StateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    is_active: bool
