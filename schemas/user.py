from pydantic import BaseModel, EmailStr
from typing import Optional

from app.schemas.state import StateResponse
from app.schemas.city import CityResponse


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str

    email: EmailStr
    phone: str

    state_id: Optional[int]
    state: Optional[StateResponse]

    city_id: Optional[int]
    city: Optional[CityResponse]

    referral_code: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
