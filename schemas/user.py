from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

from schemas.city import CityResponse


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    first_name: str
    last_name: str

    email: EmailStr
    phone: str

    city: Optional[CityResponse]

    referral_code: Optional[str]


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
