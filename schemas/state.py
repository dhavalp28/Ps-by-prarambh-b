from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StateCreate(BaseModel):
    name: str


class StateUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class StateResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
