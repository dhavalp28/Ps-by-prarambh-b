from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from schemas.state import StateResponse
from schemas.city import CityResponse


class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    alt_phone: Optional[str] = None
    gender: str  # male | female | other
    state_id: int
    city_id: int
    password: str


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    gender: Optional[str] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    is_active: Optional[bool] = None


class VendorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    alt_phone: Optional[str]
    gender: str
    state_id: int
    state: StateResponse
    city_id: int
    city: CityResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
