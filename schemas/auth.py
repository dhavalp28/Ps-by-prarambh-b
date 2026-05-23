from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterSchema(BaseModel):
    first_name: str
    last_name: str

    email: EmailStr
    phone: str

    state_id: int
    city_id: int

    referral_code: Optional[str] = None

    password: str


class LoginSchema(BaseModel):
    phone: str
    password: str
